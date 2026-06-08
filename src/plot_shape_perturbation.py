"""Plot shape perturbation distance comparison."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_results(path):
    """Read shape perturbation rows."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            rows.append(
                {
                    "variant": row["variant"],
                    "pointwise_l2": float(row["pointwise_l2"]),
                    "raw_dtw": float(row["raw_dtw"]),
                    "srvf": float(row["srvf"]),
                    "srvf_dtw": float(row["srvf_dtw"]),
                }
            )
    return rows


def plot_results(rows, output_path):
    """Plot grouped bars for distance metrics."""
    rows = [row for row in rows if row["variant"] != "identity"]
    variants = [row["variant"].replace("_", "\n") for row in rows]
    metrics = [
        ("pointwise_l2", "Pointwise L2"),
        ("raw_dtw", "Raw DTW"),
        ("srvf", "Direct SRVF"),
        ("srvf_dtw", "SRVF-DTW"),
    ]

    x = np.arange(len(rows))
    width = 0.2

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (key, label) in enumerate(metrics):
        values = [row[key] for row in rows]
        ax.bar(x + (i - 1.5) * width, values, width=width, label=label)

    ax.set_title("Metric Response to Controlled Route Perturbations")
    ax.set_xlabel("Perturbation")
    ax.set_ylabel("Distance to original trajectory")
    ax.set_xticks(x)
    ax.set_xticklabels(variants, fontsize=8)
    ax.grid(axis="y", linewidth=0.3, alpha=0.5)
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/processed/shape_perturbation.csv")
    parser.add_argument("--output", default="figures/shape_perturbation.png")
    args = parser.parse_args()

    rows = read_results(args.input)
    plot_results(rows, args.output)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
