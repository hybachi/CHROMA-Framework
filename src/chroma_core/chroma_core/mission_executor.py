"""
mission_executor.py
Breaks high-level task types into executable sequences and manages action server state.
"""

import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from chroma_interfaces.msg import Task, TaskAllocation
from chroma_interfaces.action import ExecuteMission

from chroma_core.ros_utils import get_safe_param
from chroma_core.planning.waypoints import generate_waypoints, get_task_config


class MissionExecutor(Node):
    def __init__(self):
        super().__init__("mission_executor")
        self.robot_id = get_safe_param(self, "robot_id", "unknown")
        self.current_pose = Point()
        self.current_wp_status = None
        self.cb_group = ReentrantCallbackGroup()
        self.setup_pubs_subs()
        self.get_logger().info(
            f"[{self.robot_id}] Mission Executor Action Server ready."
        )

    def setup_pubs_subs(self):
        self.create_subscription(
            Odometry, "odom", self.odom_cb, 10, callback_group=self.cb_group
        )
        self.create_subscription(
            TaskAllocation,
            "execution_status",
            self.bridge_status_cb,
            10,
            callback_group=self.cb_group,
        )
        self.execute_pub = self.create_publisher(Task, "execute_waypoint", 10)
        self.cancel_pub = self.create_publisher(Task, "cancel_waypoint", 10)
        self.action_server = ActionServer(
            self,
            ExecuteMission,
            "execute_mission",
            execute_callback=self.execute_cb,
            cancel_callback=self.cancel_cb,
            callback_group=self.cb_group,
        )

    def odom_cb(self, msg):
        self.current_pose = msg.pose.pose.position

    def bridge_status_cb(self, msg):
        self.current_wp_status = msg.status

    def cancel_cb(self, goal_handle):
        self.cancel_pub.publish(Task(task_id="HALT"))
        return CancelResponse.ACCEPT

    def _check_cancelled(self, goal_handle):
        if goal_handle.is_cancel_requested:
            self.cancel_pub.publish(Task(task_id="HALT"))
            goal_handle.canceled()
            return True
        return False

    def execute_cb(self, goal_handle):
        task = goal_handle.request.task
        strategy = (
            get_task_config().get(task.type, {}).get("strategy", "point_to_point")
        )
        waypoints = generate_waypoints(task, self.current_pose)
        total_wps = len(waypoints)

        for i, wp in enumerate(waypoints):
            if self._check_cancelled(goal_handle):
                return ExecuteMission.Result(success=False)

            self.current_wp_status = "IN_PROGRESS"
            self.execute_pub.publish(
                Task(task_id=f"{task.task_id}_WP_{i}", type="GOTO", location=wp)
            )
            goal_handle.publish_feedback(
                ExecuteMission.Feedback(
                    progress=float(i) / total_wps,
                    status_message=f"WP {i+1}/{total_wps}",
                )
            )

            while self.current_wp_status == "IN_PROGRESS":
                if self._check_cancelled(goal_handle):
                    return ExecuteMission.Result(success=False)
                time.sleep(0.1)

            if self.current_wp_status == "FAILED":
                if strategy == "point_to_point":
                    goal_handle.abort()
                    return ExecuteMission.Result(success=False)
                elif strategy == "area_sweep":
                    self.get_logger().warn("Waypoint blocked. Skipping to next.")

            if strategy == "point_to_point" and self.current_wp_status == "COMPLETED":
                if not self.wait_with_preemption(goal_handle, duration=5.0):
                    return ExecuteMission.Result(success=False)

        goal_handle.succeed()
        return ExecuteMission.Result(success=True)

    def wait_with_preemption(self, goal_handle, duration):
        for _ in range(int(duration / 0.1)):
            if goal_handle.is_cancel_requested:
                return False
            time.sleep(0.1)
        return True


def main(args=None):
    rclpy.init(args=args)
    node = MissionExecutor()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
