"""
capability_health.py
Computes capability health scores and degradation flags based on active faults.
"""

DEFAULT_FAULT_IMPACT = 0.0
DEFAULT_PENALTY_IMPACT = 0.8
DEFAULT_DEGRADED_THRESHOLD = 0.2

def compute_capability_value(base_val, cap_type, fault_map, fault_impacts, thresholds):
    fail_key = f"{cap_type.lower()}_failure"
    penalty_key = f"{cap_type.lower()}_penalty"
    
    impact = 1.0
    if fail_key in fault_map:
        impact = fault_impacts.get(fail_key, DEFAULT_FAULT_IMPACT)
    elif penalty_key in fault_map:
        impact = fault_impacts.get(penalty_key, DEFAULT_PENALTY_IMPACT)
        
    value = float(base_val * impact)
    is_degraded = value < thresholds.get(cap_type, DEFAULT_DEGRADED_THRESHOLD)
    
    return value, is_degraded