"""
ros_utils.py
Shared ROS 2 helper functions for the CHROMA bridge nodes.
"""


def get_safe_param(node, param_name, default_value):
    """Safely reads a ROS 2 parameter, returning a default if undeclared/unset."""
    if node.has_parameter(param_name):
        val = node.get_parameter(param_name).value
        return val if val is not None else default_value
    return default_value
