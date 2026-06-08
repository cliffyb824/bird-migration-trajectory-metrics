"""Plot season-aware Brownian bridge gap-reconstruction diagnostics."""

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
    "spherical_bridge": "Spherical bridge",
    "brownian_bridge_sample": "Brownian bridge samples",
}

SEASON_LABELS = {
    "spring": "Spring",
    "autumn": "Autumn",
}

PANELS = [
    ("matrix_spearman_mean", "Distance-matrix rank correlation", (0.0, 1.05)),
    ("median_relative_error_mean", "Median relative distance error", (0.0, 0.4)),
    ("cluster_ari_mean", "Cluster agreement (ARI)", (-0.1, 1.05)),
    ("anomaly_rank_spearman_mean", "Anomaly-rank correlation", (0.0, 1.05)),
]


def read_summary(path):
    """Read summarized batch diagnostics."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            converted = dict(row)
            converted["missing_fraction"] = float(row["missing_fraction"])
            for key, value in row.items():
                if key not in {"season", "method", "metric"}:
                    converted[key] = float(value)
            rows.append(converted)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/brownian_bridge_gap_reconstruction_summary.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/brownian_bridge_gap_reconstruction_batch.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    seasons = [season for season in ["spring", "autumn"] if any(row["season"] == season for row in rows)]
    if not seasons:
        seasons = sorted({row["season"] for row in rows})

    fig, axes = plt.subplots(len(PANELS), len(seasons), figsize=(6.2 * len(seasons), 12), sharex=True)
    if len(seasons) == 1:
        axes = [[axis] for axis in axes]

    colors = {"raw_dtw": "#0072B2", "srvf_dtw": "#D55E00"}
    markers = {"raw_dtw": "o", "srvf_dtw": "s"}
    linestyles = {"spherical_bridge": "--", "brownian_bridge_sample": "-"}

    for row_index, (value_key, title, ylim) in enumerate(PANELS):
        for col_index, season in enumerate(seasons):
            ax = axes[row_index][col_index]
            for method in METHOD_LABELS:
                for metric in METRIC_LABELS:
                    subset = [
                        row
                        for row in rows
                        if row["season"] == season
                        and row["method"] == method
                        and row["metric"] == metric
                    ]
                    subset.sort(key=lambda row: row["missing_fraction"])
                    if not subset:
                        continue
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
                        linewidth=1.7,
                        capsize=3,
                        label=label,
                    )
            ax.set_title(f"{SEASON_LABELS.get(season, season.title())}: {title}")
            ax.set_ylim(*ylim)
            ax.grid(alpha=0.25)
            if row_index == len(PANELS) - 1:
                ax.set_xlabel("Removed observations in one contiguous gap (%)")

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False)
    fig.text(0.01, 0.52, "Agreement with complete-data baseline", va="center", rotation="vertical")
    fig.suptitle("Season-Aware Brownian Bridge Uncertainty Under Contiguous GPS Gaps")
    fig.tight_layout(rect=(0.03, 0.08, 1, 0.96))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
