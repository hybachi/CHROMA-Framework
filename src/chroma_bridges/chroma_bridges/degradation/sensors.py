"""
sensors.py
Pure functions for injecting noise into sensor data based on degradation.
"""

import random
from sensor_msgs.msg import LaserScan


def add_scan_noise(
    msg: LaserScan, current_cap: float, baseline_cap: float = 1.0
) -> LaserScan:
    ratio = (current_cap / baseline_cap) if baseline_cap > 0 else 0.0

    if ratio >= 0.99 or baseline_cap == 0.0:
        return msg

    noise_variance = (1.0 - ratio) * 0.5
    noisy_ranges = []

    for r in msg.ranges:
        if msg.range_min < r < msg.range_max:
            noisy_r = r + random.gauss(0.0, noise_variance)
            noisy_r = max(msg.range_min, min(noisy_r, msg.range_max))
            noisy_ranges.append(noisy_r)
        else:
            noisy_ranges.append(r)

    return LaserScan(
        header=msg.header,
        angle_min=msg.angle_min,
        angle_max=msg.angle_max,
        angle_increment=msg.angle_increment,
        time_increment=msg.time_increment,
        scan_time=msg.scan_time,
        range_min=msg.range_min,
        range_max=msg.range_max,
        intensities=msg.intensities,
        ranges=noisy_ranges,
    )
