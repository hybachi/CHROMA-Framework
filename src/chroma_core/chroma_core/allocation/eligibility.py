"""
eligibility.py
Pure logic for determining if a robot is eligible to bid on a given task.
"""

DEFAULT_MIN_SCORE = 0.4
RESCUE_MULTIPLIER = 0.5
CRITICAL_FAILURE_THRESHOLD = 0.01

def check_eligibility(task_id, reqs, min_score, my_caps, degraded_states, is_rescue=False):
    min_req = min_score if min_score > 0.0 else DEFAULT_MIN_SCORE

    # Prevent total failure during emergency handoffs
    if is_rescue:
        min_req *= RESCUE_MULTIPLIER

    for req in reqs:
        my_score = my_caps.get(req, 0.0)

        if my_score <= CRITICAL_FAILURE_THRESHOLD:
            return False, f"Rejected {task_id}: {req} critically failed ({my_score:.2f})."

        if my_score < min_req:
            return False, f"Rejected {task_id}: {req} too low ({my_score:.2f} < {min_req:.2f})."

        if degraded_states.get(req, False):
            if not is_rescue:
                return False, f"Rejected {task_id}: {req} is degraded."

    # If it's a rescue but there are active degraded states, we return True but log a warning.
    if is_rescue and any(degraded_states.get(r, False) for r in reqs):
        return True, f"Warning: Bidding on {task_id} despite degraded capabilities (rescue)."

    return True, None