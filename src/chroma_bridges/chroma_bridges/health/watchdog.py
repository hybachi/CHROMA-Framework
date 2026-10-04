"""
watchdog.py
Tracks the liveliness of a specific telemetry topic.
"""
from dataclasses import dataclass

@dataclass
class WatchdogStatus:
    has_changed: bool
    is_healthy: bool

class Watchdog:
    def __init__(self, name, timeout, clock):
        self.name = name
        self.timeout = timeout
        self.clock = clock
        self.last_seen = clock.now()
        self.healthy = True

    def ping(self):
        self.last_seen = self.clock.now()

    def check(self) -> WatchdogStatus:
        """Evaluates elapsed time and returns the current health state."""
        time_since = (self.clock.now() - self.last_seen).nanoseconds / 1e9

        if time_since > self.timeout and self.healthy:
            self.healthy = False
            return WatchdogStatus(has_changed=True, is_healthy=False)
        elif time_since <= self.timeout and not self.healthy:
            self.healthy = True
            return WatchdogStatus(has_changed=True, is_healthy=True)
            
        return WatchdogStatus(has_changed=False, is_healthy=self.healthy)