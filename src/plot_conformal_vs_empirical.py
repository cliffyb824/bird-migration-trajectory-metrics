"""Plot comparison: empirical vs. conformal calibration for global BB envelopes."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


METHOD_COLORS = {
    "raw": "#E69F00",
    "empirical": "#56B4E9",
    "conformal": "#009E73",
}

SEASON_STYLES = {
    "spring": {"marker": "o", "linestyle": "-"},
    "autumn": {"marker": "s", "linestyle": "--"},
}


def read_summary(path):
    """Read summarized validation diagnostics."""
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
        default="figures/conformal_vs_empirical.png",
    )
    args = parser.parse_args()

    rows = read_summary(args.input)
    cal_rows = []
    cal_path = Path(args.cal_info)
    if cal_path.exists():
        with cal_path.open("r", encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                cal_rows.append(row)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    seasons = sorted(set(r["season"] for r in rows))
    fractions = sorted(set(r["missing_fraction"] for r in rows))
    colors = {"raw": "#E69F00", "empirical": "#56B4E9", "conformal": "#009E73"}
    labels = {
        "raw": "Raw BB (no calibration)",
        "empirical": "BB + empirical inflation (old)",
        "conformal": "BB + conformal calibration (new)",
    }

    # --- Panel A: Coverage ---
    ax = axes[0, 0]
    for season in seasons:
        season_rows = [r for r in rows if r["season"] == season]
        season_rows.sort(key=lambda r: r["missing_fraction"])
        fracs = [r["missing_fraction"] for r in season_rows]

        for method, key in [("raw", "coverage_raw"), ("empirical", "coverage_empirical_cal"), ("conformal", "coverage_conformal")]:
            vals = [r[f"{key}_mean"] for r in season_rows]
            stds = [r[f"{key}_std"] for r in season_rows]
            sty = SEASON_STYLES[season]
            label = f"{season}, {labels[method]}" if method == "raw" else None
            ax.errorbar(fracs, vals, yerr=stds, color=colors[method],
                        marker=sty["marker"], linestyle=sty["linestyle"],
                        linewidth=1.5 if method == "conformal" else 1.2,
                        capsize=3, alpha=0.8 if season == "spring" else 0.5)

    ax.axhline(y=0.90, color="black", linestyle=":", linewidth=1.0, alpha=0.4)
    ax.set_xlabel("Withheld fraction")
    ax.set_ylabel("Coverage")
    ax.set_title("(a) Pointwise envelope coverage")
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=colors["raw"], linewidth=1.5, label=labels["raw"]),
        Line2D([0], [0], color=colors["empirical"], linewidth=1.5, label=labels["empirical"]),
        Line2D([0], [0], color=colors["conformal"], linewidth=1.8, label=labels["conformal"]),
        Line2D([0], [0], marker="o", color="gray", linestyle="-", label="spring"),
        Line2D([0], [0], marker="s", color="gray", linestyle="--", label="autumn"),
    ]
    ax.legend(handles=legend_elements, fontsize=7.5, ncol=2, loc="lower left")

    # --- Panel B: Median radius ---
    ax = axes[0, 1]
    for season in seasons:
        season_rows = [r for r in rows if r["season"] == season]
        season_rows.sort(key=lambda r: r["missing_fraction"])
        fracs = [r["missing_fraction"] for r in season_rows]

        for method, key in [("raw", "median_radius_raw"), ("empirical", "median_radius_empirical_cal"), ("conformal", "median_radius_conformal")]:
            vals = [r[f"{key}_mean"] for r in season_rows]
            sty = SEASON_STYLES[season]
            ax.plot(fracs, vals, color=colors[method],
                    marker=sty["marker"], linestyle=sty["linestyle"],
                    linewidth=1.5 if method == "conformal" else 1.2,
                    alpha=0.8 if season == "spring" else 0.5)

    ax.set_xlabel("Withheld fraction")
    ax.set_ylabel("Radius (km)")
    ax.set_title("(b) Median envelope radius")
    ax.grid(alpha=0.3)

    # --- Panel C: Calibration factors ---
    ax = axes[1, 0]
    if cal_rows:
        q_hats = {}
        for row in cal_rows:
            q_hats[row["season"]] = float(row["q_hat"])

        for season in seasons:
            season_rows = [r for r in rows if r["season"] == season]
            season_rows.sort(key=lambda r: r["missing_fraction"])
            fracs = [r["missing_fraction"] for r in season_rows]
            infl_vals = [r["radius_inflation_mean"] for r in season_rows]
            sty = SEASON_STYLES[season]
            ax.plot(fracs, infl_vals, color=colors["empirical"],
                    marker=sty["marker"], linestyle=sty["linestyle"],
                    linewidth=1.2, alpha=0.8,
                    label=f"{season}, empirical inflation")

        # Horizontal lines for conformal q_hat
        for season, q in q_hats.items():
            ax.axhline(y=q, color=colors["conformal"],
                       linestyle="--" if season == "autumn" else "-",
                       linewidth=1.5,
                       label=f"{season}, conformal $\\hat{{q}}$ = {q:.1f}")

    ax.set_xlabel("Withheld fraction")
    ax.set_ylabel("Calibration factor")
    ax.set_title("(c) Empirical inflation vs. conformal quantile")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # --- Panel D: State-conditioned scales ---
    ax = axes[1, 1]
    if cal_rows:
        states = ["resting", "foraging", "directed"]
        state_labels = ["Resting", "Foraging", "Directed"]
        state_colors = ["#999999", "#56B4E9", "#0072B2"]
        y_pos = np.arange(len(states))
        bar_width = 0.25

        for si, season in enumerate(seasons):
            sub = [r for r in cal_rows if r["season"] == season]
            if not sub:
                continue
            row = sub[0]
            scale_values = [float(row.get(f"{s}_scale", 0)) for s in states]
            global_val = float(row.get("global_scale", 0))
            offset = (si - 0.5) * bar_width
            ax.barh(y_pos + offset, scale_values, bar_width * 0.9,
                    color=state_colors, alpha=0.85 if si == 0 else 0.5,
                    label=f"{season}" if si == 0 else None)
            ax.axvline(x=global_val,
                       color="#E69F00" if season == "spring" else "#D55E00",
                       linestyle="--", linewidth=1.5,
                       label=f"{season} global ({global_val:.4f})")

        ax.set_yticks(y_pos)
        ax.set_yticklabels(state_labels)
        ax.set_xlabel("Perturbation scale $\\sigma$")
        ax.set_title("(d) State-conditioned perturbation scales")
        ax.legend(fontsize=7.5, loc="lower right")

    fig.tight_layout()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
