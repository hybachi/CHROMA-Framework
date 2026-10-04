"""
telemetry_bridge.py
Monitors raw robot telemetry topics to infer capability health.
"""

import rclpy
import importlib
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from chroma_interfaces.msg import Capability, TaskAllocation

from chroma_bridges.ros_utils import get_safe_param
from chroma_bridges.health.watchdog import Watchdog
from chroma_bridges.health.battery_sim import BatterySimulator

QOS_PRESETS = {
    "reliable": QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    ),
    "best_effort": QoSProfile(
        reliability=ReliabilityPolicy.BEST_EFFORT,
        history=HistoryPolicy.KEEP_LAST,
        depth=10,
    ),
}


class TelemetryBridge(Node):
    def __init__(self):
        super().__init__(
            "telemetry_bridge",
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True,
        )
        self.robot_id = get_safe_param(self, "robot_id", "unknown")
        self.baselines = {
            k: v.value for k, v in self.get_parameters_by_prefix("capabilities").items()
        }
        self.has_battery = get_safe_param(self, "telemetry.has_battery", False)
        self.watchdogs = {}

        if self.has_battery:
            self.setup_real_battery()
        else:
            self.setup_sim_battery()

        self.setup_watchdogs()
        self.telemetry_pub = self.create_publisher(Capability, "telemetry", 10)
        self.create_timer(0.5, self.evaluate_health)

        self.get_logger().info(f"[{self.robot_id}] Telemetry Bridge Active")

    def setup_real_battery(self):
        self.v_max = get_safe_param(self, "telemetry.battery_v_max", 12.6)
        self.v_min = get_safe_param(self, "telemetry.battery_v_min", 11.1)
        battery_topic = get_safe_param(self, "telemetry.battery_topic", "battery_state")
        self.create_subscription(BatteryState, battery_topic, self.battery_cb, 10)

    def setup_sim_battery(self):
        drain_idle = get_safe_param(self, "telemetry.drain_rate_idle", 0.0005)
        drain_active = get_safe_param(self, "telemetry.drain_rate_active", 0.002)
        self.bat_sim = BatterySimulator(
            self.baselines.get("BATTERY", 1.0), drain_idle, drain_active
        )
        self.create_subscription(TaskAllocation, "/swarm/allocation", self.alloc_cb, 10)

    def setup_watchdogs(self):
        topics = get_safe_param(self, "telemetry.watchdogs.topics", [])
        types = get_safe_param(self, "telemetry.watchdogs.types", [])
        caps = get_safe_param(self, "telemetry.watchdogs.capabilities", [])
        timeouts = get_safe_param(self, "telemetry.watchdogs.timeouts", [])
        reliability = get_safe_param(
            self, "telemetry.watchdogs.reliability", ["reliable"] * len(topics)
        )

        for i, topic in enumerate(topics):
            msg_class = self.get_msg_class(types[i])
            if msg_class is None:
                continue

            cap_name = caps[i]
            qos_profile = QOS_PRESETS.get(
                reliability[i] if i < len(reliability) else "reliable",
                QOS_PRESETS["reliable"],
            )

            self.watchdogs[cap_name] = Watchdog(cap_name, timeouts[i], self.get_clock())

            callback = lambda msg, c=cap_name: self.watchdogs[c].ping()
            self.create_subscription(msg_class, topic, callback, qos_profile)

    def battery_cb(self, msg):
        normalized = max(
            0.0, min(1.0, (msg.voltage - self.v_min) / (self.v_max - self.v_min))
        )
        self.publish_cap("BATTERY", normalized)

    def alloc_cb(self, msg):
        if msg.robot_id == self.robot_id:
            self.bat_sim.set_active(msg.status == "ASSIGNED")

    def evaluate_health(self):
        if not self.has_battery:
            self.publish_cap("BATTERY", self.bat_sim.step())

        for cap_name, wd in self.watchdogs.items():
            status = wd.check()
            if status.has_changed:
                if not status.is_healthy:
                    self.get_logger().warn(
                        f"Watchdog: {cap_name} timed out! Degrading capability"
                    )
                    self.publish_cap(cap_name, 0.1)
                else:
                    self.get_logger().info(f"Watchdog: {cap_name} recovered!")
                    self.publish_cap(cap_name, self.baselines.get(cap_name, 1.0))

    def publish_cap(self, type_string, value):
        self.telemetry_pub.publish(Capability(type=type_string, value=float(value)))

    def get_msg_class(self, type_string):
        try:
            parts = type_string.split(".")
            module = importlib.import_module(".".join(parts[:-1]))
            return getattr(module, parts[-1])
        except Exception as e:
            self.get_logger().error(f"Dynamic import error for {type_string}: {e}")
            return None


def main(args=None):
    rclpy.init(args=args)
    node = TelemetryBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
