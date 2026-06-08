"""Plot the controlled time-warp robustness experiment."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_results(path):
    """Read time-warp robustness CSV rows."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            rows.append(
                {
                    "trajectory_id": row["trajectory_id"],
                    "gamma": float(row["gamma"]),
                    "pointwise_l2": float(row["pointwise_l2"]),
                    "raw_dtw": float(row["raw_dtw"]),
                    "srvf": float(row["srvf"]),
                    "srvf_dtw": float(row["srvf_dtw"]),
                }
            )
    return rows


def plot_results(rows, output_path):
    """Plot distance response to monotone time warping."""
    rows = sorted(rows, key=lambda row: row["gamma"])
    gammas = [row["gamma"] for row in rows]
    pointwise = [row["pointwise_l2"] for row in rows]
    raw_dtw = [row["raw_dtw"] for row in rows]
    srvf = [row["srvf"] for row in rows]
    srvf_dtw = [row["srvf_dtw"] for row in rows]
    trajectory_id = rows[0]["trajectory_id"] if rows else ""

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.plot(gammas, pointwise, marker="o", linewidth=2, label="Pointwise L2")
    ax.plot(gammas, raw_dtw, marker="D", linewidth=2, label="Raw-coordinate DTW")
    ax.plot(gammas, srvf, marker="s", linewidth=2, label="Direct SRVF")
    ax.plot(gammas, srvf_dtw, marker="^", linewidth=2, label="SRVF-DTW")
    ax.axvline(1.0, color="0.5", linestyle="--", linewidth=1)
    ax.set_title("Distance Sensitivity Under Artificial Time Warping")
    ax.set_xlabel("Time-warp exponent gamma")
    ax.set_ylabel("Distance to original trajectory")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend(frameon=False)
    ax.text(
        0.02,
        0.02,
        f"Trajectory: {trajectory_id}",
        transform=ax.transAxes,
        fontsize=8,
        color="0.35",
    )
    fig.tight_layout()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/timewarp_robustness.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/timewarp_robustness.png",
    )
    args = parser.parse_args()

    rows = read_results(args.input)
    plot_results(rows, args.output)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
