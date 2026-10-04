"""
battery_sim.py
Simulates battery depletion based on robot activity state.
"""

class BatterySimulator:
    def __init__(self, initial_level=1.0, drain_idle=0.0005, drain_active=0.002):
        self.level = initial_level
        self.drain_idle = drain_idle
        self.drain_active = drain_active
        self.is_active = False

    def set_active(self, active: bool):
        self.is_active = active

    def step(self):
        drain = self.drain_active if self.is_active else self.drain_idle
        self.level = max(0.0, self.level - drain)
        return self.level