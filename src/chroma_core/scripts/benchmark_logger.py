#!/usr/bin/env python3
import rclpy
import csv
import os
import time
from rclpy.node import Node
from chroma_interfaces.msg import SwarmStatus, TaskAllocation, Bid


class BenchmarkLogger(Node):
    def __init__(self):
        super().__init__("benchmark_logger")
        os.makedirs("chroma_logs", exist_ok=True)
        ts = int(time.time())
        self.f_status = open(f"chroma_logs/status_{ts}.csv", "a", newline="")
        self.f_alloc = open(f"chroma_logs/allocations_{ts}.csv", "a", newline="")
        self.f_bids = open(f"chroma_logs/bids_{ts}.csv", "a", newline="")

        self.w_status = csv.writer(self.f_status)
        self.w_alloc = csv.writer(self.f_alloc)
        self.w_bids = csv.writer(self.f_bids)

        self.w_status.writerow(["time", "robot_id", "cap_type", "value", "is_degraded"])
        self.w_alloc.writerow(["time", "task_id", "robot_id", "status"])
        self.w_bids.writerow(["time", "task_id", "robot_id", "score"])

        self.create_subscription(SwarmStatus, "/swarm/status", self.stat_cb, 10)
        self.create_subscription(TaskAllocation, "/swarm/allocation", self.alloc_cb, 10)
        self.create_subscription(Bid, "/swarm/bids", self.bid_cb, 10)
        self.get_logger().info("Benchmark Logger Active. Writing to chroma_logs/")

    def stat_cb(self, msg):
        t = self.get_clock().now().nanoseconds / 1e9
        for c in msg.capabilities:
            self.w_status.writerow([t, msg.robot_id, c.type, c.value, c.is_degraded])

    def alloc_cb(self, msg):
        t = self.get_clock().now().nanoseconds / 1e9
        self.w_alloc.writerow([t, msg.task_id, msg.robot_id, msg.status])

    def bid_cb(self, msg):
        t = self.get_clock().now().nanoseconds / 1e9
        self.w_bids.writerow([t, msg.task_id, msg.robot_id, msg.score])


def main():
    rclpy.init()
    n = BenchmarkLogger()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    finally:
        n.f_status.close()
        n.f_alloc.close()
        n.f_bids.close()


if __name__ == "__main__":
    main()
