"""
scenarios.py
Pure dictionary definitions of task scenarios for reproducible benchmarks.
"""

from geometry_msgs.msg import Point

def create_point(x, y, z=0.0):
    return Point(x=float(x), y=float(y), z=float(z))

SCENARIOS = {
    "nominal": [
        {
            "id": "NOMINAL_SEARCH",
            "type": "SEARCH",
            "location": create_point(0.0, 1.5),
            "target_area": [create_point(0.5, 2.0)]
        },
        {
            "id": "NOMINAL_DELIVERY",
            "type": "DELIVERY",
            "location": create_point(0.0, -1.5),
            "target_area": [create_point(0.0, -2.5, 0.0)]
        }
    ],
    "benchmark": [
        {
            "id": "BENCHMARK_DEBRIS",
            "type": "SEARCH",
            "location": create_point(0.5, 3.5),
            "target_area": [create_point(3.5, 1.0)]
        }
    ],
    "stress": [
        {
            "id": "STRESS_CASCADE",
            "type": "DELIVERY",
            "location": create_point(-2.5, 1.0),
            "target_area": [create_point(-3.5, 1.5, 0.0)]
        }
    ]
}