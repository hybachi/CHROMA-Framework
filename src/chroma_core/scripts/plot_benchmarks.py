#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys


def main():
    try:
        f_stat = sorted(glob.glob("logs/status_*.csv"))[-1]
    except IndexError:
        print("No logs found.")
        sys.exit(1)

    df = pd.read_csv(f_stat)
    df["time"] = df["time"] - df["time"].min()  # Normalize time

    plt.figure(figsize=(10, 6))
    for (rid, cap), group in df.groupby(["robot_id", "cap_type"]):
        if cap in ["MOBILITY", "PERCEPTION", "PAYLOAD"]:
            plt.plot(group["time"], group["value"], label=f"{rid} {cap}")

    plt.xlabel("Time (s)")
    plt.ylabel("Capability Score")
    plt.title("Robot Health Over Mission")
    plt.legend()
    plt.grid()
    plt.savefig("chroma_logs/benchmark_plot.png")
    print("Plot saved to chroma_logs/benchmark_plot.png")


if __name__ == "__main__":
    main()
