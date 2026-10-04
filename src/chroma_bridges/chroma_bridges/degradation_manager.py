"""
degradation_manager.py
Simulates hardware degradation by scaling physical commands and sensor data.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from chroma_interfaces.msg import SwarmStatus

from chroma_bridges.ros_utils import get_safe_param
from chroma_bridges.degradation.motion import throttle_twist
from chroma_bridges.degradation.sensors import add_scan_noise


class DegradationManager(Node):
    def __init__(self):
        super().__init__(
            "degradation_manager",
            allow_undeclared_parameters=True,
            automatically_declare_parameters_from_overrides=True,
        )
        self.robot_id = get_safe_param(self, "robot_id", "unknown")

        # Determine which capabilities map to which degradation behaviors dynamically
        self.target_motion = get_safe_param(
            self, "degradation_targets.velocity", "MOBILITY"
        )
        self.target_laser = get_safe_param(
            self, "degradation_targets.laser", "PERCEPTION"
        )

        yaml_caps = {
            k: v.value for k, v in self.get_parameters_by_prefix("capabilities").items()
        }

        self.baselines = {
            self.target_motion: yaml_caps.get(self.target_motion, 1.0),
            self.target_laser: yaml_caps.get(self.target_laser, 1.0),
        }

        self.caps = self.baselines.copy()
        self.last_cmd_vel = Twist()

        self.create_subscription(SwarmStatus, "/swarm/status", self.status_cb, 10)
        self.create_subscription(Twist, "cmd_vel", self.cmd_vel_cb, 10)
        self.vel_pub = self.create_publisher(Twist, "cmd_vel_degraded", 10)
        self.create_subscription(
            LaserScan, "scan_raw", self.scan_cb, qos_profile_sensor_data
        )
        self.scan_pub = self.create_publisher(
            LaserScan, "scan", qos_profile_sensor_data
        )

        self.get_logger().info(f"[{self.robot_id}] Degradation Manager Active")

    def status_cb(self, msg):
        if msg.robot_id != self.robot_id:
            return

        for cap in msg.capabilities:
            if cap.type in self.caps and self.caps[cap.type] != cap.value:
                self.caps[cap.type] = cap.value
                self.get_logger().info(f"{cap.type} changed to: {cap.value:.2f}")

                # Re-evaluate twist immediately if motion capability drops
                if cap.type == self.target_motion:
                    self.cmd_vel_cb(self.last_cmd_vel)

    def cmd_vel_cb(self, msg):
        self.last_cmd_vel = msg
        throttled_msg = throttle_twist(
            msg,
            self.caps.get(self.target_motion, 1.0),
            self.baselines.get(self.target_motion, 1.0),
        )
        self.vel_pub.publish(throttled_msg)

    def scan_cb(self, msg):
        degraded_msg = add_scan_noise(
            msg,
            self.caps.get(self.target_laser, 1.0),
            self.baselines.get(self.target_laser, 1.0),
        )
        self.scan_pub.publish(degraded_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DegradationManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
