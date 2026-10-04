#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from std_msgs.msg import String


class FaultInjector(Node):
    def __init__(self):
        super().__init__("fault_injector_script")

    def trigger(self, robot_id, fault):
        pub = self.create_publisher(String, f"/{robot_id}/inject_fault", 10)
        time.sleep(0.5)  # Wait for discovery
        pub.publish(String(data=fault))
        self.get_logger().info(f"Triggered {fault} on {robot_id}")


def main():
    rclpy.init()
    n = FaultInjector()

    print("Executing Mobility Fault Scenario...")
    time.sleep(10)
    n.trigger("tb3_1", "mobility_penalty")
    time.sleep(15)
    n.trigger("tb3_1", "reset")

    n.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
