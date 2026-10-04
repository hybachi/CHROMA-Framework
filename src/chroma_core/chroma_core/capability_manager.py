"""
capability_manager.py
Maintains and publishes the robot's hardware capability health scores.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from chroma_interfaces.msg import SwarmStatus, Capability
from chroma_core.ros_utils import get_safe_param
from chroma_core.capability_health import compute_capability_value

class CapabilityManager(Node):
    def __init__(self):
        super().__init__('capability_manager', allow_undeclared_parameters=True, automatically_declare_parameters_from_overrides=True)
        self.setup_params()
        self.setup_state()
        self.setup_pubs_subs()
        self.get_logger().info(f"[{self.robot_id}] Tracking: {list(self.caps.keys())}")

    def setup_params(self):
        self.robot_id = get_safe_param(self, 'robot_id', 'unknown')
        self.robot_type = get_safe_param(self, 'robot_type', 'UGV')

    def setup_state(self):
        self.fault_map = {}
        self.latest_rejection = ""
        self.caps = {k: v.value for k, v in self.get_parameters_by_prefix('capabilities').items()}
        self.thresholds = {k: v.value for k, v in self.get_parameters_by_prefix('thresholds').items()}
        self.fault_impacts = {k: v.value for k, v in self.get_parameters_by_prefix('fault_impacts').items()}

    def setup_pubs_subs(self):
        self.create_subscription(Capability, 'telemetry', self.telemetry_cb, 10)
        self.create_subscription(String, 'inject_fault', self.fault_cb, 10)
        self.create_subscription(String, 'latest_rejection', self.rejection_cb, 10)
        
        swarm_qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL, history=HistoryPolicy.KEEP_LAST, depth=1)
        self.swarm_pub = self.create_publisher(SwarmStatus, '/swarm/status', swarm_qos)
        self.create_timer(5.0, self.publish_state) 

    def telemetry_cb(self, msg):
        self.caps[msg.type] = msg.value

    def fault_cb(self, msg):
        if msg.data == "reset":
            self.fault_map.clear()
        else:
            self.fault_map[msg.data] = True
        self.publish_state()

    def rejection_cb(self, msg):
        self.latest_rejection = msg.data
        self.publish_state()

    def publish_state(self):
        msg = SwarmStatus(robot_id=self.robot_id, robot_type=self.robot_type, latest_rejection_reason=self.latest_rejection)
        msg.header.stamp = self.get_clock().now().to_msg()
        for cap_type, base_val in self.caps.items():
            val, is_deg = compute_capability_value(base_val, cap_type, self.fault_map, self.fault_impacts, self.thresholds)
            msg.capabilities.append(Capability(type=cap_type, value=val, is_degraded=is_deg))
        self.swarm_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CapabilityManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()