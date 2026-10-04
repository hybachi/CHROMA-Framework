"""
task_allocator.py
Distributed bidding, task assignment, and preemption for a single robot.
"""

import rclpy
import random
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point
from chroma_interfaces.msg import Task, Bid, TaskAllocation, SwarmStatus, SwarmLog
from chroma_interfaces.action import ExecuteMission

from chroma_core.ros_utils import schedule_timer, destroy_timer_safely, get_safe_param
from chroma_core.allocation.eligibility import check_eligibility
from chroma_core.allocation.scoring import calculate_score
from chroma_core.allocation.auction_book import AuctionBook

BID_DELAY_MIN, BID_DELAY_MAX = 0.1, 0.5
PREEMPT_RETRY_DELAY = 0.5
AUCTION_WINDOW = 2.0
HEALTH_CHECK_INTERVAL = 2.0


class TaskAllocator(Node):
    def __init__(self):
        super().__init__("task_allocator")
        self.robot_id = get_safe_param(self, "robot_id", "tb3_0")

        # Robot State
        self.my_caps = {}
        self.my_degraded_states = {}
        self.current_pose = Point()

        # Auction & Bid Bookkeeping
        self.auction_book = AuctionBook()
        self.bid_timers = {}
        self.auction_timers = {}
        self.preempt_timers = {}

        # Active Task State
        self.active_task = None
        self.mission_goal_handle = None

        # Preemption State
        self.is_preempting = False
        self.preempting_tasks = set()

        self.setup_pubs_subs()
        self.create_timer(HEALTH_CHECK_INTERVAL, self.health_check)

    def setup_pubs_subs(self):
        self.create_subscription(SwarmStatus, "/swarm/status", self.cap_cb, 10)
        self.create_subscription(Task, "/mission/tasks", self.task_cb, 10)
        self.create_subscription(Bid, "/swarm/bids", self.bid_cb, 10)
        self.create_subscription(TaskAllocation, "/swarm/allocation", self.alloc_cb, 10)
        self.create_subscription(Odometry, "odom", self.odom_cb, 10)

        self.bid_pub = self.create_publisher(Bid, "/swarm/bids", 10)
        self.log_pub = self.create_publisher(SwarmLog, "/swarm/logs", 10)
        self.task_pub = self.create_publisher(Task, "/mission/tasks", 10)
        self.alloc_pub = self.create_publisher(TaskAllocation, "/swarm/allocation", 10)
        self.rejection_pub = self.create_publisher(String, "latest_rejection", 10)

        self.mission_client = ActionClient(
            self, ExecuteMission, f"/{self.robot_id}/execute_mission"
        )

    def odom_cb(self, msg):
        self.current_pose = msg.pose.pose.position

    def bid_cb(self, msg):
        self.auction_book.record_bid(msg.task_id, msg.robot_id, msg.score)

    def cap_cb(self, msg):
        if msg.robot_id == self.robot_id:
            for cap in msg.capabilities:
                self.my_caps[cap.type] = cap.value
                self.my_degraded_states[cap.type] = cap.is_degraded

    def alloc_cb(self, msg):
        if msg.status == "CANCELLED":
            self.clear_task_state(msg.task_id)
            if self.active_task and self.active_task.task_id == msg.task_id:
                self.halt_execution()
        elif msg.status == "PREEMPT_REQUEST":
            self.preempting_tasks.add(msg.task_id)
            self.auction_book.clear_auction_state(msg.task_id)
            if msg.robot_id != self.robot_id:
                self.auction_book.unassign_task(msg.task_id)
        elif msg.status == "ABORTED":
            if self.auction_book.get_assigned_robot(msg.task_id) == msg.robot_id:
                self.clear_task_state(msg.task_id)
        elif msg.status == "ASSIGNED":
            self.auction_book.assign_task(msg.task_id, msg.robot_id)
            self.preempting_tasks.discard(msg.task_id)
            if (
                self.active_task
                and self.active_task.task_id == msg.task_id
                and self.is_preempting
            ):
                if msg.robot_id != self.robot_id:
                    self.publish_log(f"Handoff verified. Yielding to {msg.robot_id}.")
                    self.halt_execution()
                else:
                    self.is_preempting = False
        elif msg.status == "COMPLETED" and msg.robot_id == self.robot_id:
            self.active_task = None
            self.is_preempting = False
            self.mission_goal_handle = None

    def task_cb(self, task):
        is_rescue = task.task_id in self.preempting_tasks
        if not is_rescue and self.auction_book.is_assigned(task.task_id):
            return
        if (
            task.task_id in self.auction_book.tasks_bid_on
            or task.task_id in self.auction_book.pending_auctions
        ):
            return
        if self.active_task is not None and self.active_task.task_id != task.task_id:
            return

        reqs = list(task.required_capabilities)
        if "BATTERY" not in reqs:
            reqs.append("BATTERY")

        eligible, reason = check_eligibility(
            task.task_id,
            reqs,
            task.min_capability_score,
            self.my_caps,
            self.my_degraded_states,
            is_rescue,
        )
        if reason:
            self.get_logger().info(reason)
            self.rejection_pub.publish(String(data=reason))
        if not eligible:
            return

        self.auction_book.tasks_bid_on.add(task.task_id)
        schedule_timer(
            self,
            self.bid_timers,
            task.task_id,
            random.uniform(BID_DELAY_MIN, BID_DELAY_MAX),
            lambda: self.submit_bid(task, reqs),
        )

    def health_check(self):
        if self.active_task is None or self.is_preempting:
            return
        reqs = list(self.active_task.required_capabilities)
        if "BATTERY" not in reqs:
            reqs.append("BATTERY")

        for req in reqs:
            if self.my_degraded_states.get(req, False):
                self.publish_log(
                    f"Degradation in {req}. Initiating preemption for {self.active_task.task_id}.",
                    SwarmLog.WARN,
                )
                self.request_preemption(self.active_task)
                return

    def request_preemption(self, task):
        self.is_preempting = True
        self.publish_allocation(task.task_id, "PREEMPT_REQUEST")
        self.auction_book.bids_received.pop(task.task_id, None)
        schedule_timer(
            self,
            self.preempt_timers,
            task.task_id,
            PREEMPT_RETRY_DELAY,
            lambda: self.task_pub.publish(task),
        )

    def submit_bid(self, task, reqs):
        is_my_rescue = (
            self.is_preempting
            and self.active_task
            and self.active_task.task_id == task.task_id
        )
        if self.active_task is not None and not is_my_rescue:
            return
        if not is_my_rescue and (
            task.task_id in self.auction_book.pending_auctions
            or self.auction_book.is_assigned(task.task_id)
        ):
            return

        my_score = calculate_score(
            task, reqs, self.my_caps, self.my_degraded_states, self.current_pose
        )
        self.bid_pub.publish(
            Bid(task_id=task.task_id, robot_id=self.robot_id, score=my_score)
        )
        self.auction_book.record_bid(task.task_id, self.robot_id, my_score)
        self.auction_book.pending_auctions.add(task.task_id)

        self.publish_log(f"Bid {my_score:.2f} on {task.task_id}.")
        schedule_timer(
            self,
            self.auction_timers,
            task.task_id,
            AUCTION_WINDOW,
            lambda: self.resolve_auction(task),
        )

    def resolve_auction(self, task):
        if task.task_id not in self.auction_book.pending_auctions:
            return
        is_my_rescue = (
            self.is_preempting
            and self.active_task
            and self.active_task.task_id == task.task_id
        )
        if not is_my_rescue and self.auction_book.is_assigned(task.task_id):
            self.auction_book.pending_auctions.discard(task.task_id)
            return

        winner_id, top_score = self.auction_book.get_winner(task.task_id)
        self.auction_book.pending_auctions.discard(task.task_id)
        self.auction_book.tasks_bid_on.discard(task.task_id)

        if winner_id == self.robot_id:
            if is_my_rescue:
                self.is_preempting = False
            else:
                self.publish_log(f"Won Task {task.task_id}.")
                self.claim_task(task)
        elif winner_id:
            if is_my_rescue:
                self.halt_execution()

    def claim_task(self, task):
        self.active_task = task
        self.is_preempting = False
        self.auction_book.assign_task(task.task_id, self.robot_id)
        self.publish_allocation(task.task_id, "ASSIGNED")

        self.rejection_pub.publish(String(data="Assigned to Task"))

        goal = ExecuteMission.Goal(task=task)
        self.mission_client.wait_for_server()
        future = self.mission_client.send_goal_async(goal)
        future.add_done_callback(self.goal_accepted_cb)

    def goal_accepted_cb(self, future):
        self.mission_goal_handle = future.result()
        if not self.mission_goal_handle.accepted:
            self.active_task = None
            return
        result_future = self.mission_goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_cb)

    def goal_result_cb(self, future):
        result = future.result().result
        status = future.result().status

        if status == 5 or not result.success:
            if self.active_task is not None:
                self.publish_log(
                    f"Execution failed. Re-auctioning {self.active_task.task_id}.",
                    SwarmLog.ERROR,
                )
                self.publish_allocation(self.active_task.task_id, "ABORTED")
                self.task_pub.publish(self.active_task)
        else:
            self.publish_log(f"{self.active_task.task_id} COMPLETED.", SwarmLog.INFO)
            self.publish_allocation(self.active_task.task_id, "COMPLETED")

        if self.active_task:
            self.auction_book.bids_received.pop(self.active_task.task_id, None)
        self.active_task = None
        self.mission_goal_handle = None

    def clear_task_state(self, task_id):
        self.auction_book.clear_auction_state(task_id)
        self.auction_book.unassign_task(task_id)
        self.preempting_tasks.discard(task_id)
        destroy_timer_safely(self, self.bid_timers, task_id)
        destroy_timer_safely(self, self.auction_timers, task_id)

    def halt_execution(self):
        if self.mission_goal_handle:
            self.mission_goal_handle.cancel_goal_async()
            self.mission_goal_handle = None
        if self.active_task:
            self.clear_task_state(self.active_task.task_id)
        self.active_task = None
        self.is_preempting = False

    def publish_allocation(self, task_id, status):
        self.alloc_pub.publish(
            TaskAllocation(task_id=task_id, robot_id=self.robot_id, status=status)
        )

    def publish_log(self, message, level=SwarmLog.INFO):
        self.get_logger().info(message)
        self.log_pub.publish(
            SwarmLog(level=level, robot_id=self.robot_id, message=message)
        )


def main(args=None):
    rclpy.init(args=args)
    node = TaskAllocator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
