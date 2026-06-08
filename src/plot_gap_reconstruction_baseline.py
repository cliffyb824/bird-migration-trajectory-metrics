"""Plot contiguous-gap reconstruction baseline diagnostics."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


METRIC_LABELS = {
    "raw_dtw": "Raw DTW",
    "srvf_dtw": "SRVF-DTW",
}

METHOD_LABELS = {
    "observed_only": "Observed points only",
    "spherical_bridge": "Spherical bridge",
}

PANELS = [
    ("matrix_spearman_mean", "Distance-matrix rank correlation", (0.0, 1.05)),
    ("median_relative_error_mean", "Median relative distance error", (0.0, 0.3)),
    ("cluster_ari_mean", "Cluster agreement (ARI)", (-0.05, 1.05)),
    ("anomaly_rank_spearman_mean", "Anomaly-rank correlation", (0.0, 1.05)),
]


def read_summary(path):
    """Read summarized reconstruction diagnostics."""
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
        default="data/processed/gap_reconstruction_baseline_summary.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/gap_reconstruction_baseline.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)
    colors = {"raw_dtw": "#E69F00", "srvf_dtw": "#D55E00"}
    markers = {"raw_dtw": "o", "srvf_dtw": "s"}
    linestyles = {"observed_only": "--", "spherical_bridge": "-"}

    for ax, (value_key, title, ylim) in zip(axes.flat, PANELS):
        for method in METHOD_LABELS:
            for metric in METRIC_LABELS:
                subset = [
                    row
                    for row in rows
                    if row["reconstruction_method"] == method and row["metric"] == metric
                ]
                subset.sort(key=lambda row: row["missing_fraction"])
                x = [100 * row["missing_fraction"] for row in subset]
                y = [row[value_key] for row in subset]
                std_key = value_key.replace("_mean", "_std")
                yerr = [row[std_key] for row in subset]
                label = f"{METRIC_LABELS[metric]}, {METHOD_LABELS[method]}"
                ax.errorbar(
                    x,
                    y,
                    yerr=yerr,
                    color=colors[metric],
                    marker=markers[metric],
                    linestyle=linestyles[method],
                    linewidth=1.8,
                    capsize=3,
                    label=label,
                )
        ax.set_title(title)
        ax.set_ylim(*ylim)
        ax.grid(alpha=0.25)

    for ax in axes[1]:
        ax.set_xlabel("Removed observations in one contiguous gap (%)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Agreement with complete-data baseline")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False)
    fig.suptitle("Simple Reconstruction Baselines for Contiguous GPS Gaps")
    fig.tight_layout(rect=(0, 0.1, 1, 0.95))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
