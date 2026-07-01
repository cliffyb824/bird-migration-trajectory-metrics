"""Plot comparison of global BB, behavior-aware BB, and behavior+conformal methods."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


METHOD_LABELS = {
    "global": "Global BB",
    "behavior": "Behavior BB",
    "behavior_conformal": "Behavior BB + Conformal",
}

METHOD_COLORS = {
    "global": "#E69F00",
    "behavior": "#56B4E9",
    "behavior_conformal": "#009E73",
}

SEASON_HATCHES = {
    "spring": "",
    "autumn": "//",
}

PANEL_METRICS = [
    ("coverage", "Coverage at 90% nominal", (0.0, 1.05)),
    ("median_radius", "Median envelope radius (km)", None),
    ("center_error", "Mean center reconstruction error (km)", None),
]


def read_summary(path):
    """Read summarized combined validation diagnostics."""
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            converted = {}
            for key, value in row.items():
                try:
                    converted[key] = float(value)
                except (ValueError, TypeError):
                    converted[key] = value
            rows.append(converted)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/behavior_aware_validation_summary.csv",
    )
    parser.add_argument(
        "--cal-info",
        default="data/processed/behavior_aware_calibration_info.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/behavior_aware_comparison.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)

    # Also read calibration info for state scale panel
    cal_rows = []
    cal_path = Path(args.cal_info)
    if cal_path.exists():
        with cal_path.open("r", encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                cal_rows.append(row)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    methods = ["global", "behavior", "behavior_conformal"]
    seasons = sorted(set(r["season"] for r in rows))
    fractions = sorted(set(r["missing_fraction"] for r in rows))
    n_methods = len(methods)
    n_fracs = len(fractions)
    bar_width = 0.22
    x = np.arange(n_fracs)

    # --- Panel A: Coverage ---
    ax = axes[0, 0]
    for mi, method in enumerate(methods):
        for si, season in enumerate(seasons):
            key = f"{method}_coverage_mean"
            values = []
            errors = []
            for frac in fractions:
                sub = [r for r in rows
                       if r["season"] == season and abs(r["missing_fraction"] - frac) < 1e-6]
                if sub:
                    values.append(sub[0].get(key, 0))
                    errors.append(sub[0].get(key.replace("_mean", "_std"), 0))
                else:
                    values.append(0)
                    errors.append(0)
            offset = (mi - 1) * bar_width + (si - 0.5) * bar_width * 0.4
            bars = ax.bar(
                x + offset, values, bar_width * 0.35,
                color=METHOD_COLORS[method],
                alpha=0.85 if si == 0 else 0.5,
                hatch=SEASON_HATCHES[season] if si > 0 else "",
                label=f"{METHOD_LABELS[method]}, {season}" if mi == 0 or si == 0 else None,
            )
    ax.axhline(y=0.90, color="black", linestyle="--", linewidth=1.0, alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(f*100)}%" for f in fractions])
    ax.set_ylabel("Coverage")
    ax.set_title("(a) Pointwise envelope coverage")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    ax.grid(axis="y", alpha=0.3)

    # --- Panel B: Median radius ---
    ax = axes[0, 1]
    for mi, method in enumerate(methods):
        key = f"{method}_median_radius_mean"
        for si, season in enumerate(seasons):
            values = []
            for frac in fractions:
                sub = [r for r in rows
                       if r["season"] == season and abs(r["missing_fraction"] - frac) < 1e-6]
                values.append(sub[0].get(key, 0) if sub else 0)
            offset = (mi - 1) * bar_width + (si - 0.5) * bar_width * 0.4
            ax.bar(
                x + offset, values, bar_width * 0.35,
                color=METHOD_COLORS[method],
                alpha=0.85 if si == 0 else 0.5,
                hatch=SEASON_HATCHES[season] if si > 0 else "",
            )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(f*100)}%" for f in fractions])
    ax.set_ylabel("Radius (km)")
    ax.set_title("(b) Median envelope radius")
    ax.grid(axis="y", alpha=0.3)

    # --- Panel C: Center error ---
    ax = axes[1, 0]
    for mi, method in enumerate(methods):
        key = f"{method}_center_error_mean"
        for si, season in enumerate(seasons):
            values = []
            for frac in fractions:
                sub = [r for r in rows
                       if r["season"] == season and abs(r["missing_fraction"] - frac) < 1e-6]
                values.append(sub[0].get(key, 0) if sub else 0)
            offset = (mi - 1) * bar_width + (si - 0.5) * bar_width * 0.4
            ax.bar(
                x + offset, values, bar_width * 0.35,
                color=METHOD_COLORS[method],
                alpha=0.85 if si == 0 else 0.5,
                hatch=SEASON_HATCHES[season] if si > 0 else "",
            )
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(f*100)}%" for f in fractions])
    ax.set_ylabel("Error (km)")
    ax.set_xlabel("Withheld fraction")
    ax.set_title("(c) Mean center reconstruction error")
    ax.grid(axis="y", alpha=0.3)

    # --- Panel D: State-conditioned scales ---
    ax = axes[1, 1]
    if cal_rows:
        states = ["resting", "foraging", "directed"]
        state_labels = ["Resting", "Foraging", "Directed"]
        state_colors = ["#999999", "#56B4E9", "#0072B2"]
        y_pos = np.arange(len(states))

        for si, season in enumerate(seasons):
            sub = [r for r in cal_rows if r["season"] == season]
            if not sub:
                continue
            row = sub[0]
            scale_values = [float(row.get(f"{s}_scale", 0)) for s in states]
            global_val = float(row.get("global_scale", 0))
            offset = (si - 0.5) * 0.3
            ax.barh(
                y_pos + offset, scale_values, 0.28,
                color=state_colors,
                alpha=0.85 if si == 0 else 0.5,
                hatch=SEASON_HATCHES[season] if si > 0 else "",
                label=f"{season}" if si == 0 else None,
            )
            if si == 0:
                ax.axvline(x=global_val, color="#E69F00", linestyle="--", linewidth=1.5,
                           label=f"Global scale ({global_val:.4f})")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(state_labels)
        ax.set_xlabel("Perturbation scale σ")
        ax.set_title("(d) State-conditioned bridge scales")
        ax.legend(fontsize=8)
        ax.grid(axis="x", alpha=0.3)

    fig.tight_layout()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
