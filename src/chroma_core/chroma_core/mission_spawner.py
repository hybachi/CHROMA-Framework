#!/usr/bin/env python3

"""
mission_spawner.py
Automated mission dispatcher for reproducible thesis benchmarking.

Author: H.A. Sharif
Year: 2026
"""

import sys
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from chroma_interfaces.msg import Task

class MissionSpawner(Node):
    def __init__(self):
        super().__init__('mission_spawner')
        
        # QoS profile with a queue size of 10
        self.task_pub = self.create_publisher(Task, '/mission/tasks', 10)
        
        # Allow DDS discovery to connect publishers and subscribers
        self.get_logger().info("Waiting 2 seconds for DDS network discovery...")
        time.sleep(2.0)

    def create_point(self, x, y, z=0.0):
        p = Point()
        p.x = float(x)
        p.y = float(y)
        p.z = float(z)
        return p

    def publish_task(self, task_id, task_type, reqs, min_score, loc, target_area=None):
        msg = Task()
        msg.task_id = task_id
        msg.type = task_type
        msg.priority = 1.0
        msg.required_capabilities = reqs
        msg.min_capability_score = min_score
        msg.location = loc
        
        if target_area:
            msg.target_area = target_area
            
        self.task_pub.publish(msg)
        self.get_logger().info(f"Published Task: {task_id} at ({loc.x}, {loc.y})")

    def run_nominal(self):
        """Phase 1: Proves initial math works in the Safe Zone (x=0, y=0)"""
        self.get_logger().info("--- INITIATING NOMINAL VALIDATION ---")
        
        # SEARCH Task -> Best for TB3 (Needs Perception/Mobility)
        self.publish_task(
            task_id="NOMINAL_SEARCH",
            task_type="SEARCH",
            reqs=["PERCEPTION", "MOBILITY"],
            min_score=0.4,
            loc=self.create_point(0.0, 1.5),
            target_area=[self.create_point(0.5, 2.0)]
        )

        time.sleep(0.5) # Slight stagger

        # DELIVERY Task -> Best for JetHexa (Needs Payload/Mobility)
        self.publish_task(
            task_id="NOMINAL_DELIVERY",
            task_type="DELIVERY",
            reqs=["PAYLOAD", "MOBILITY"],
            min_score=0.4,
            loc=self.create_point(0.0, -1.5),
            target_area=[self.create_point(0.0, -2.5, 0.0)] # z acts as yaw
        )

    def run_benchmark(self):
        """Phase 2: The Core A/B Test (Debris Field x=1.0 to 4.0)"""
        self.get_logger().info("--- INITIATING A/B BENCHMARK ---")
        
        # Deep in the Debris Field. TB3 will win the bid, enter zone, and degrade.
        self.publish_task(
            task_id="BENCHMARK_DEBRIS",
            task_type="SEARCH",
            reqs=["PERCEPTION", "MOBILITY"],
            min_score=0.4,
            loc=self.create_point(0.5, 3.5),
            target_area=[self.create_point(3.5, 1.0)]
        )

    def run_stress(self):
        """Phase 3: Systemic Stress Test (Collapsed Office x=-4.0 to -1.0)"""
        self.get_logger().info("--- INITIATING STRESS TEST (COLLAPSED OFFICE) ---")
        
        # Deep in the Office. JetHexa gets penalized here. 
        self.publish_task(
            task_id="STRESS_CASCADE",
            task_type="DELIVERY",
            reqs=["PAYLOAD", "MOBILITY"],
            min_score=0.4,
            loc=self.create_point(-2.5, 1.0),
            target_area=[self.create_point(-3.5, 1.5, 0.0)]
        )

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) < 2:
        print("Usage: ros2 run chroma_core mission_spawner.py [nominal | benchmark | stress]")
        sys.exit(1)

    scenario = sys.argv[1].lower()
    spawner = MissionSpawner()

    if scenario == "nominal":
        spawner.run_nominal()
    elif scenario == "benchmark":
        spawner.run_benchmark()
    elif scenario == "stress":
        spawner.run_stress()
    else:
        spawner.get_logger().error(f"Unknown scenario: {scenario}")
        print("Available scenarios: nominal, benchmark, stress")

    # Allow time for the network to flush the published messages before exiting
    time.sleep(1.0)
    
    spawner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()