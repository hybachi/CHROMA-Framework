"""
waypoints.py
Breaks high-level task types into executable, geometric waypoints using task_types.yaml.
"""

import os
import math
import yaml
from geometry_msgs.msg import Point
from ament_index_python.packages import get_package_share_directory

SEARCH_STEP_SIZE = 0.5
_CONFIG_CACHE = None


def get_task_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        try:
            pkg_share = get_package_share_directory("chroma_bringup")
            config_path = os.path.join(pkg_share, "config", "task_types.yaml")
            with open(config_path, "r") as f:
                _CONFIG_CACHE = yaml.safe_load(f).get("tasks", {})
        except Exception:
            _CONFIG_CACHE = {}
    return _CONFIG_CACHE


def generate_waypoints(task, current_pose):
    p1 = task.location
    p2 = task.target_area[0] if len(task.target_area) > 0 else p1

    configs = get_task_config()
    strategy = configs.get(task.type, {}).get("strategy", "point_to_point")

    if strategy == "point_to_point":
        yaw_ab = math.atan2(p2.y - p1.y, p2.x - p1.x)
        p1.z, p2.z = yaw_ab, yaw_ab
        return [p1, p2]
    elif strategy == "area_sweep":
        return build_search_pattern(p1, p2, current_pose)
    return [p1]


def build_search_pattern(p1, p2, current_pose):
    min_x, max_x = min(p1.x, p2.x), max(p1.x, p2.x)
    min_y, max_y = min(p1.y, p2.y), max(p1.y, p2.y)
    corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    cx, cy = current_pose.x, current_pose.y
    start_x, start_y = min(corners, key=lambda c: math.hypot(c[0] - cx, c[1] - cy))

    raw_points = []
    if (max_x - min_x) >= (max_y - min_y):
        y_dir = 1 if start_y == min_y else -1
        curr_y, curr_x = start_y, start_x
        while min_y <= curr_y <= max_y:
            raw_points.append((curr_x, curr_y))
            curr_x = max_x if curr_x == min_x else min_x
            curr_y += SEARCH_STEP_SIZE * y_dir
    else:
        x_dir = 1 if start_x == min_x else -1
        curr_x, curr_y = start_x, start_y
        while min_x <= curr_x <= max_x:
            raw_points.append((curr_x, curr_y))
            curr_y = max_y if curr_y == min_y else min_y
            curr_x += SEARCH_STEP_SIZE * x_dir
    return apply_orientations(raw_points)


def apply_orientations(raw_points):
    waypoints = []
    for i in range(len(raw_points)):
        x1, y1 = raw_points[i]
        yaw = (
            math.atan2(raw_points[i + 1][1] - y1, raw_points[i + 1][0] - x1)
            if i < len(raw_points) - 1
            else (waypoints[-1].z if waypoints else 0.0)
        )
        waypoints.append(Point(x=float(x1), y=float(y1), z=float(yaw)))
    return waypoints
