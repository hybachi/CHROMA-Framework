#!/usr/bin/env python3
import os
import yaml
from glob import glob


def validate_profiles():
    base_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "chroma_bringup", "config", "profiles"
    )
    profiles = glob(os.path.join(base_dir, "*.yaml"))

    errors = 0
    for p in profiles:
        with open(p, "r") as f:
            data = yaml.safe_load(f).get("/**", {}).get("ros__parameters", {})

        caps = data.get("capabilities", {})
        thresholds = data.get("thresholds", {})
        impacts = data.get("fault_impacts", {})
        watchdogs = data.get("telemetry", {}).get("watchdogs", {})

        # Watchdog arrays equal length
        if watchdogs:
            lens = [
                len(watchdogs.get(k, []))
                for k in ["topics", "types", "capabilities", "timeouts"]
            ]
            if len(set(lens)) > 1:
                print(
                    f"[ERROR] {os.path.basename(p)}: Watchdog array lengths mismatch {lens}"
                )
                errors += 1

        # Threshold keys in capabilities
        for t in thresholds.keys():
            if t not in caps:
                print(
                    f"[ERROR] {os.path.basename(p)}: Threshold '{t}' not found in capabilities"
                )
                errors += 1

        # Fault impact keys correctly named
        for imp in impacts.keys():
            base = imp.replace("_failure", "").replace("_penalty", "").upper()
            if base not in caps:
                print(
                    f"[ERROR] {os.path.basename(p)}: Fault impact '{imp}' refers to unknown cap '{base}'"
                )
                errors += 1

    if errors == 0:
        print("✅ All YAML profiles validated successfully.")
    else:
        print(f"❌ Found {errors} validation errors.")
        exit(1)


if __name__ == "__main__":
    validate_profiles()
