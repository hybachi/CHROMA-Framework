import os
import sys
import time
import yaml
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from chroma_interfaces.msg import Task
from chroma_core.scenarios import SCENARIOS

class MissionSpawner(Node):
    def __init__(self):
        super().__init__('mission_spawner')
        self.task_pub = self.create_publisher(Task, '/mission/tasks', 10)
        self.task_configs = self.load_task_configs()
        self.get_logger().info("Waiting 2 seconds for DDS network discovery...")
        time.sleep(2.0)

    def load_task_configs(self):
        try:
            pkg_share = get_package_share_directory('chroma_bringup')
            config_path = os.path.join(pkg_share, 'config', 'task_types.yaml')
            with open(config_path, 'r') as f:
                return yaml.safe_load(f).get('tasks', {})
        except Exception as e:
            self.get_logger().error(f"Failed to load task_types.yaml: {e}")
            return {}

    def spawn_scenario(self, scenario_name):
        if scenario_name not in SCENARIOS:
            self.get_logger().error(f"Unknown scenario: {scenario_name}")
            return

        self.get_logger().info(f"--- INITIATING {scenario_name.upper()} SCENARIO ---")

        for task_def in SCENARIOS[scenario_name]:
            task_type = task_def["type"]
            cfg = self.task_configs.get(task_type, {})

            msg = Task()
            msg.task_id = task_def["id"]
            msg.type = task_type
            msg.priority = 1.0
            msg.required_capabilities = cfg.get("requires", [])
            msg.min_capability_score = cfg.get("min_score", 0.4)
            msg.location = task_def["location"]
            if "target_area" in task_def:
                msg.target_area = task_def["target_area"]

            self.task_pub.publish(msg)
            self.get_logger().info(f"Published Task: {msg.task_id} at ({msg.location.x}, {msg.location.y})")
            time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) < 2:
        print("Usage: ros2 run chroma_core mission_spawner [nominal | benchmark | stress]")
        sys.exit(1)

    scenario = sys.argv[1].lower()
    spawner = MissionSpawner()
    spawner.spawn_scenario(scenario)

    time.sleep(1.0)
    spawner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()