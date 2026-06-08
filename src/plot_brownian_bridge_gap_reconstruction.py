"""Plot Brownian bridge gap-reconstruction uncertainty diagnostics."""

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

PANELS = [
    ("matrix_spearman", "Distance-matrix rank correlation", (0.0, 1.05)),
    ("median_relative_error", "Median relative distance error", (0.0, 0.35)),
    ("cluster_ari", "Cluster agreement (ARI)", (-0.1, 1.05)),
    ("anomaly_rank_spearman", "Anomaly-rank correlation", (0.0, 1.05)),
]


def read_summary(path):
    """Read summarized Brownian bridge diagnostics."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            converted = dict(row)
            for key, value in row.items():
                if key not in {"method", "metric"}:
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
        default="figures/brownian_bridge_gap_reconstruction_summary.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.5))
    x_positions = {
        ("raw_dtw", "spherical_bridge"): 0.8,
        ("raw_dtw", "brownian_bridge_sample"): 1.2,
        ("srvf_dtw", "spherical_bridge"): 1.8,
        ("srvf_dtw", "brownian_bridge_sample"): 2.2,
    }
    colors = {"spherical_bridge": "#E69F00", "brownian_bridge_sample": "#CC79A7"}
    markers = {"spherical_bridge": "o", "brownian_bridge_sample": "s"}

    for ax, (prefix, title, ylim) in zip(axes.flat, PANELS):
        for row in rows:
            metric = row["metric"]
            method = row["method"]
            x = x_positions[(metric, method)]
            mean = row[f"{prefix}_mean"]
            low = row[f"{prefix}_p05"]
            high = row[f"{prefix}_p95"]
            ax.errorbar(
                [x],
                [mean],
                yerr=[[mean - low], [high - mean]],
                color=colors[method],
                marker=markers[method],
                markersize=7,
                capsize=4,
                linestyle="none",
                label=METHOD_LABELS[method],
            )
        ax.set_title(title)
        ax.set_xlim(0.45, 2.55)
        ax.set_ylim(*ylim)
        ax.set_xticks([1.0, 2.0], [METRIC_LABELS["raw_dtw"], METRIC_LABELS["srvf_dtw"]])
        ax.grid(axis="y", alpha=0.25)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    fig.legend(unique.values(), unique.keys(), loc="lower center", ncol=2, frameon=False)
    fig.suptitle("Movement-Aware Brownian Bridge Samples for Contiguous GPS Gaps")
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
