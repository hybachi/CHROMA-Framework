"""
ros_utils.py
Shared ROS 2 helper functions for the CHROMA core nodes.
"""


def schedule_timer(node, timer_dict, task_id, delay, callback):
    """Safely schedules a timer, canceling any existing timer for the same task."""
    destroy_timer_safely(node, timer_dict, task_id)

    def on_fire():
        destroy_timer_safely(node, timer_dict, task_id)
        callback()

    timer_dict[task_id] = node.create_timer(delay, on_fire)


def destroy_timer_safely(node, timer_dict, task_id):
    """Safely destroys a timer if it exists."""
    timer = timer_dict.pop(task_id, None)
    if timer:
        try:
            if not timer.is_canceled():
                timer.cancel()
            node.destroy_timer(timer)
        except Exception:
            pass


def get_safe_param(node, param_name, default_value):
    """Safely reads a ROS 2 parameter, declaring it if necessary."""
    if not node.has_parameter(param_name):
        node.declare_parameter(param_name, default_value)

    val = node.get_parameter(param_name).value
    return val if val is not None else default_value
