"""
motion.py
Pure functions for simulating kinematic degradation.
"""

from geometry_msgs.msg import Twist


def throttle_twist(msg: Twist, current_cap: float, baseline_cap: float = 1.0) -> Twist:
    raw_ratio = (current_cap / baseline_cap) if baseline_cap > 0 else 0.0
    ratio = raw_ratio**2.5

    throttled_msg = Twist()
    throttled_msg.linear.x = msg.linear.x * ratio
    throttled_msg.linear.y = msg.linear.y * ratio
    throttled_msg.angular.z = msg.angular.z * ratio

    return throttled_msg
