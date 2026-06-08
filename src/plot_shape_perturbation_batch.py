"""Plot batch shape perturbation summary."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_summary(path):
    """Read batch perturbation summary rows."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            converted = {"variant": row["variant"]}
            for key, value in row.items():
                if key != "variant":
                    converted[key] = float(value)
            rows.append(converted)
    return rows


def plot_summary(rows, output_path):
    """Plot grouped bars with standard deviation error bars."""
    variants = [row["variant"].replace("_", "\n") for row in rows]
    metrics = [
        ("pointwise_l2", "Pointwise L2"),
        ("raw_dtw", "Raw DTW"),
        ("srvf", "Direct SRVF"),
        ("srvf_dtw", "SRVF-DTW"),
    ]

    x = np.arange(len(rows))
    width = 0.2
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for i, (key, label) in enumerate(metrics):
        means = [row[f"{key}_mean"] for row in rows]
        stds = [row[f"{key}_std"] for row in rows]
        ax.bar(
            x + (i - 1.5) * width,
            means,
            width=width,
            yerr=stds,
            capsize=2,
            label=label,
        )

    n = int(rows[0]["n_trajectories"]) if rows else 0
    ax.set_title("Mean Metric Response to Controlled Route Perturbations")
    ax.set_xlabel("Perturbation")
    ax.set_ylabel("Distance to original trajectory")
    ax.set_xticks(x)
    ax.set_xticklabels(variants, fontsize=8)
    ax.grid(axis="y", linewidth=0.3, alpha=0.5)
    ax.legend(frameon=False, ncol=2)
    ax.text(
        0.02,
        0.95,
        f"n = {n} trajectories; error bars show +/- 1 SD",
        transform=ax.transAxes,
        fontsize=8,
        color="0.35",
        va="top",
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
        default="data/processed/shape_perturbation_batch_summary.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/shape_perturbation_batch.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    plot_summary(rows, args.output)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
