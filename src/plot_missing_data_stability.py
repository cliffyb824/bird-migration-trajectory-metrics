"""Plot trajectory-metric stability under missing tracking observations."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


METRIC_LABELS = {
    "raw_dtw": "Raw DTW",
    "srvf_dtw": "SRVF-DTW",
}

MECHANISM_LABELS = {
    "random_points": "Random missing points",
    "contiguous_gap": "Contiguous missing gap",
}

PANELS = [
    ("matrix_spearman_mean", "Distance-matrix rank correlation", (0.0, 1.05)),
    ("cluster_ari_mean", "Cluster agreement (ARI)", (-0.05, 1.05)),
    ("anomaly_rank_spearman_mean", "Anomaly-rank correlation", (0.0, 1.05)),
    ("top_k_overlap_mean", "Top-5 anomaly overlap", (0.0, 1.05)),
]


def read_summary(path):
    """Read summarized stability diagnostics."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            converted = dict(row)
            converted["missing_fraction"] = float(row["missing_fraction"])
            for key, value in row.items():
                if key.endswith("_mean") or key.endswith("_std"):
                    converted[key] = float(value)
            rows.append(converted)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/missing_data_stability_summary.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/missing_data_stability.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)
    colors = {"raw_dtw": "#E69F00", "srvf_dtw": "#D55E00"}
    markers = {"raw_dtw": "o", "srvf_dtw": "s"}
    linestyles = {"random_points": "-", "contiguous_gap": "--"}

    for ax, (value_key, title, ylim) in zip(axes.flat, PANELS):
        for mechanism in MECHANISM_LABELS:
            for metric in METRIC_LABELS:
                subset = [
                    row
                    for row in rows
                    if row["missing_mechanism"] == mechanism and row["metric"] == metric
                ]
                subset.sort(key=lambda row: row["missing_fraction"])
                x = [100 * row["missing_fraction"] for row in subset]
                y = [row[value_key] for row in subset]
                std_key = value_key.replace("_mean", "_std")
                yerr = [row[std_key] for row in subset]
                label = f"{METRIC_LABELS[metric]}, {MECHANISM_LABELS[mechanism]}"
                ax.errorbar(
                    x,
                    y,
                    yerr=yerr,
                    color=colors[metric],
                    marker=markers[metric],
                    linestyle=linestyles[mechanism],
                    linewidth=1.8,
                    capsize=3,
                    label=label,
                )
        ax.set_title(title)
        ax.set_ylim(*ylim)
        ax.grid(alpha=0.25)

    for ax in axes[1]:
        ax.set_xlabel("Removed observations (%)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Stability relative to complete data")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False)
    fig.suptitle("Sensitivity of Migration-Route Analysis to Missing GPS Observations")
    fig.tight_layout(rect=(0, 0.1, 1, 0.95))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
