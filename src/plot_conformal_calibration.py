"""Plot conformal calibration diagnostics for trajectory envelopes.

Shows: (a) nonconformity score distribution with q_hat,
       (b) coverage before/after calibration,
       (c) empirical vs. conformal calibration factors.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


SEASON_COLORS = {"spring": "#0072B2", "autumn": "#D55E00"}
SEASON_MARKERS = {"spring": "o", "autumn": "s"}


def read_rows(path):
    """Read per-gap validation rows."""
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
        default="data/processed/behavior_aware_validation.csv",
    )
    parser.add_argument(
        "--summary-input",
        default="data/processed/behavior_aware_validation_summary.csv",
    )
    parser.add_argument(
        "--cal-info-input",
        default="data/processed/behavior_aware_calibration_info.csv",
    )
    parser.add_argument(
        "--output",
        default="figures/conformal_calibration.png",
    )
    args = parser.parse_args()

    rows = read_rows(args.input)
    summaries = read_summary(args.summary_input)

    # Read calibration info for q_hat and scales
    cal_info = {}
    cal_path = Path(args.cal_info_input)
    if cal_path.exists():
        with cal_path.open("r", encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                cal_info[row["season"]] = row

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

    # --- Panel A: Nonconformity score distribution (from per-gap data) ---
    ax = axes[0]
    eval_rows = [r for r in rows if r.get("phase") == "evaluation"]

    # Reconstruct scores: s = center_error / median_radius
    all_scores_by_season = {}
    for row in eval_rows:
        season = row.get("season", "")
        center_err = float(row.get("sample_center_mean_error_km", 0))
        radius = float(row.get("median_radius_km", 1.0))
        score = center_err / max(radius, 1e-9)
        all_scores_by_season.setdefault(season, []).append(score)

    for season, scores in all_scores_by_season.items():
        scores_arr = np.array(scores)
        # Filter extreme outliers for visualization
        p95 = np.percentile(scores_arr, 95)
        plot_scores = scores_arr[scores_arr <= p95]

        ax.hist(
            plot_scores, bins=25, alpha=0.5,
            color=SEASON_COLORS.get(season, "gray"),
            label=f"{season} (n={len(scores_arr)})"
        )

        # q_hat line
        if season in cal_info:
            q_hat = float(cal_info[season].get("q_hat", 0))
            ax.axvline(
                x=q_hat, color=SEASON_COLORS.get(season, "black"),
                linestyle="--", linewidth=2.0,
                label=f"{season}: $\\hat{{q}}$ = {q_hat:.2f}"
            )

    ax.set_xlabel("Nonconformity score ($s = e / r$)")
    ax.set_ylabel("Count")
    ax.set_title("(a) Per-gap nonconformity scores")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    # --- Panel B: Coverage before/after calibration ---
    ax = axes[1]
    seasons = sorted(set(r["season"] for r in summaries))

    for season in seasons:
        season_rows = [r for r in summaries if r["season"] == season]
        season_rows.sort(key=lambda r: r["missing_fraction"])
        fracs = [r["missing_fraction"] for r in season_rows]

        # Raw coverage
        raw_cov = [r["coverage_raw_mean"] for r in season_rows]
        raw_std = [r["coverage_raw_std"] for r in season_rows]

        # Conformal coverage
        conf_cov = [r["coverage_conformal_mean"] for r in season_rows]
        conf_std = [r["coverage_conformal_std"] for r in season_rows]

        color = SEASON_COLORS.get(season, "black")
        marker = SEASON_MARKERS.get(season, "o")

        ax.errorbar(
            fracs, raw_cov, yerr=raw_std,
            color=color, marker=marker, linestyle="-",
            linewidth=1.5, capsize=3, alpha=0.6,
            label=f"{season}, raw BB"
        )
        ax.errorbar(
            fracs, conf_cov, yerr=conf_std,
            color=color, marker=marker, linestyle="--",
            linewidth=1.8, capsize=3,
            label=f"{season}, BB + conformal"
        )

    ax.axhline(y=0.90, color="black", linestyle=":", linewidth=1.0, alpha=0.4)
    ax.set_xlabel("Withheld fraction")
    ax.set_ylabel("Empirical coverage")
    ax.set_title("(b) Coverage before/after conformal calibration")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7.5, ncol=2)
    ax.grid(alpha=0.3)

    # Annotation
    ax.text(
        0.98, 0.92, "target: 90%",
        transform=ax.transAxes, ha="right", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5)
    )

    # --- Panel C: Empirical vs conformal calibration factors ---
    ax = axes[2]

    for season in seasons:
        season_rows = [r for r in summaries if r["season"] == season]
        season_rows.sort(key=lambda r: r["missing_fraction"])
        fracs = [r["missing_fraction"] * 100 for r in season_rows]

        infl_vals = [r["radius_inflation_mean"] for r in season_rows]
        infl_std = [r["radius_inflation_std"] for r in season_rows]

        color = SEASON_COLORS.get(season, "black")
        marker = SEASON_MARKERS.get(season, "o")

        ax.errorbar(
            fracs, infl_vals, yerr=infl_std,
            color=color, marker=marker, linestyle="-",
            linewidth=1.5, capsize=3, alpha=0.7,
            label=f"{season}, empirical inflation"
        )

    # Conformal q_hat as horizontal lines
    for season in seasons:
        if season in cal_info:
            q_hat = float(cal_info[season]["q_hat"])
            color = SEASON_COLORS.get(season, "black")
            ax.axhline(
                y=q_hat, color=color, linestyle="--",
                linewidth=2.0, alpha=0.6,
                label=f"{season}, conformal $\\hat{{q}} = {q_hat:.2f}$"
            )

    ax.set_xlabel("Withheld fraction (%)")
    ax.set_ylabel("Calibration factor")
    ax.set_title("(c) Empirical inflation vs. conformal quantile")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
