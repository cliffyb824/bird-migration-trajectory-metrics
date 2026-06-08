"""Plot batch time-warp robustness summary."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_summary(path):
    """Read batch summary rows."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            rows.append({key: float(value) for key, value in row.items()})
    return sorted(rows, key=lambda row: row["gamma"])


def plot_metric(ax, gammas, mean, std, label, marker):
    """Plot a mean line with one-standard-deviation band."""
    mean = np.asarray(mean, dtype=float)
    std = np.asarray(std, dtype=float)
    ax.plot(gammas, mean, marker=marker, linewidth=2, label=label)
    ax.fill_between(gammas, mean - std, mean + std, alpha=0.15)


def plot_summary(rows, output_path):
    """Plot batch robustness summary."""
    gammas = np.asarray([row["gamma"] for row in rows], dtype=float)
    n = int(rows[0]["n_trajectories"]) if rows else 0

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    plot_metric(
        ax,
        gammas,
        [row["pointwise_l2_mean"] for row in rows],
        [row["pointwise_l2_std"] for row in rows],
        "Pointwise L2",
        "o",
    )
    plot_metric(
        ax,
        gammas,
        [row["raw_dtw_mean"] for row in rows],
        [row["raw_dtw_std"] for row in rows],
        "Raw-coordinate DTW",
        "D",
    )
    plot_metric(
        ax,
        gammas,
        [row["srvf_mean"] for row in rows],
        [row["srvf_std"] for row in rows],
        "Direct SRVF",
        "s",
    )
    plot_metric(
        ax,
        gammas,
        [row["srvf_dtw_mean"] for row in rows],
        [row["srvf_dtw_std"] for row in rows],
        "SRVF-DTW",
        "^",
    )
    ax.axvline(1.0, color="0.5", linestyle="--", linewidth=1)
    ax.set_title("Mean Distance Sensitivity Under Time Warping")
    ax.set_xlabel("Time-warp exponent gamma")
    ax.set_ylabel("Distance to original trajectory")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend(frameon=False)
    ax.text(
        0.02,
        0.02,
        f"n = {n} trajectories; bands show +/- 1 SD",
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
        default="data/processed/timewarp_robustness_batch_summary.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/timewarp_robustness_batch.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    plot_summary(rows, args.output)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
