"""
scoring.py
Pure math for calculating auction bid scores based on capabilities and distance.
"""

DISTANCE_WEIGHT = 0.2
DEGRADATION_PENALTY = 0.25

def calculate_score(task, reqs, my_caps, degraded_states, current_pose):
    avg_cap = sum(my_caps.get(r, 0.0) for r in reqs) / max(1, len(reqs))
    
    # Manhattan distance
    dist = abs(task.location.x - current_pose.x) + abs(task.location.y - current_pose.y)
    
    # Score heavily weights capabilities, slightly weights distance
    score = float(avg_cap * (1.0 / (1.0 + dist * DISTANCE_WEIGHT)))

    # Ensure healthier peers win degraded auctions (penalty)
    for req in reqs:
        if degraded_states.get(req, False):
            return score * DEGRADATION_PENALTY

    return score