"""Plot normalized responses from the controlled perturbation sweep."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METRICS = [
    ("pointwise_l2", "Pointwise L2"),
    ("raw_dtw", "Raw DTW"),
    ("srvf", "Direct SRVF"),
    ("srvf_dtw", "SRVF-DTW"),
]
PERTURBATIONS = [
    ("smoothed", "Smoothing window"),
    ("local_detour", "Detour amplitude"),
    ("local_loop", "Loop amplitude"),
]


def read_summary(paths):
    """Read one or more sweep summary tables."""
    rows = []
    for path in paths:
        with Path(path).open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            for row in reader:
                converted = {
                    "season": row["season"],
                    "perturbation": row["perturbation"],
                }
                for key, value in row.items():
                    if key not in converted:
                        converted[key] = float(value)
                rows.append(converted)
    return rows


def plot_summary(rows, output_path):
    """Plot metric-specific responses relative to strong time-warp controls."""
    seasons = list(OrderedDict.fromkeys(row["season"] for row in rows))
    fig, axes = plt.subplots(
        len(seasons),
        len(PERTURBATIONS),
        figsize=(12, 3.8 * len(seasons)),
        squeeze=False,
    )

    for row_index, season in enumerate(seasons):
        season_rows = [row for row in rows if row["season"] == season]
        n = int(season_rows[0]["n_trajectories"]) if season_rows else 0
        for column_index, (perturbation, xlabel) in enumerate(PERTURBATIONS):
            ax = axes[row_index, column_index]
            perturbation_rows = [
                row for row in season_rows if row["perturbation"] == perturbation
            ]
            perturbation_rows.sort(key=lambda row: row["intensity"])
            x = np.asarray([row["intensity"] for row in perturbation_rows], dtype=float)
            for metric, label in METRICS:
                medians = np.asarray(
                    [row[f"{metric}_relative_median"] for row in perturbation_rows],
                    dtype=float,
                )
                ax.plot(x, medians, marker="o", linewidth=1.8, label=label)
            ax.axhline(1.0, color="0.45", linestyle="--", linewidth=1)
            ax.set_yscale("log", base=2)
            ax.set_xlabel(xlabel)
            ax.grid(axis="y", linewidth=0.3, alpha=0.5)
            ax.set_title(f"{season.capitalize()}: {perturbation.replace('_', ' ')}")
            if column_index == 0:
                ax.set_ylabel("Median response / time-warp baseline")
            ax.text(
                0.03,
                0.95,
                f"n = {n}",
                transform=ax.transAxes,
                fontsize=8,
                color="0.35",
                va="top",
            )

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        frameon=False,
        ncol=4,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.965),
    )
    fig.suptitle(
        "Metric-Specific Response Relative to Strong Time-Warp Controls",
        y=0.995,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs="+", required=True)
    parser.add_argument(
        "--output",
        default="figures/shape_perturbation_sweep_relative.png",
    )
    args = parser.parse_args()

    plot_summary(read_summary(args.input), args.output)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
