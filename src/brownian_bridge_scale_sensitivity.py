"""Sensitivity analysis for Brownian bridge perturbation scale."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from brownian_bridge_gap_reconstruction import (
    estimate_global_bridge_scale,
    run_experiment_for_input,
)
from missing_data_stability import read_trajectory_points, select_trajectories


DIAGNOSTICS = [
    "matrix_spearman",
    "median_relative_error",
    "cluster_ari",
    "anomaly_rank_spearman",
    "top_k_overlap",
]


def summarize_rows(rows):
    """Summarize sensitivity rows by season, scale multiplier, method, and metric."""
    grouped = {}
    for row in rows:
        key = (
            row["season"],
            row["scale_multiplier"],
            row["method"],
            row["metric"],
        )
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (season, multiplier, method, metric), group in grouped.items():
        summary = {
            "season": season,
            "scale_multiplier": multiplier,
            "method": method,
            "metric": metric,
            "n_samples": len(group),
            "n_trajectories": group[0]["n_trajectories"],
            "bridge_scale": float(np.mean([row["bridge_scale"] for row in group])),
        }
        for diagnostic in DIAGNOSTICS:
            values = np.asarray([row[diagnostic] for row in group], dtype=float)
            summary[f"{diagnostic}_mean"] = float(np.nanmean(values))
            summary[f"{diagnostic}_std"] = (
                float(np.nanstd(values, ddof=1)) if len(values) > 1 else 0.0
            )
        summaries.append(summary)
    return summaries


def write_rows(path, rows):
    """Write scale-sensitivity rows."""
    fieldnames = [
        "season",
        "scale_multiplier",
        "missing_fraction",
        "repeat",
        "method",
        "metric",
        "sample",
        "bridge_scale",
        "n_trajectories",
        "n_points",
        *DIAGNOSTICS,
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summaries(path, rows):
    """Write summarized scale sensitivity diagnostics."""
    fieldnames = [
        "season",
        "scale_multiplier",
        "method",
        "metric",
        "n_samples",
        "n_trajectories",
        "bridge_scale",
    ]
    for diagnostic in DIAGNOSTICS:
        fieldnames.extend([f"{diagnostic}_mean", f"{diagnostic}_std"])
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def estimate_scale(input_path, max_trajectories, min_points, max_span):
    """Estimate a seasonal bridge scale using the same estimator as the main experiment."""
    groups = read_trajectory_points(input_path)
    selected = select_trajectories(groups, min_points, max_trajectories)
    return estimate_global_bridge_scale(selected, max_span=max_span)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spring-input",
        default="data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
    )
    parser.add_argument(
        "--autumn-input",
        default="data/processed/lbbg_zeebrugge_transit_autumn_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/brownian_bridge_scale_sensitivity.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="data/processed/brownian_bridge_scale_sensitivity_summary.csv",
    )
    parser.add_argument("--scale-multipliers", nargs="+", type=float, default=[0.5, 1.0, 2.0])
    parser.add_argument("--max-trajectories", type=int, default=12)
    parser.add_argument("--min-points", type=int, default=100)
    parser.add_argument("--n-points", type=int, default=50)
    parser.add_argument("--n-clusters", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--missing-fraction", type=float, default=0.6)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--bridge-samples", type=int, default=6)
    parser.add_argument("--scale-max-span", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260607)
    args = parser.parse_args()

    input_specs = [
        ("spring", args.spring_input),
        ("autumn", args.autumn_input),
    ]
    base_scales = {
        season: estimate_scale(
            input_path,
            args.max_trajectories,
            args.min_points,
            args.scale_max_span,
        )
        for season, input_path in input_specs
    }

    rows = []
    for season, input_path in input_specs:
        for multiplier in args.scale_multipliers:
            run_args = SimpleNamespace(
                min_points=args.min_points,
                max_trajectories=args.max_trajectories,
                n_points=args.n_points,
                n_clusters=args.n_clusters,
                top_k=args.top_k,
                missing_fractions=[args.missing_fraction],
                repeats=args.repeats,
                bridge_samples=args.bridge_samples,
                bridge_scale=base_scales[season] * multiplier,
                estimate_bridge_scale=False,
                scale_max_span=args.scale_max_span,
                sample_plot="figures/brownian_bridge_scale_sensitivity_samples.png",
            )
            rng_seed = args.seed + int(round(multiplier * 1000))
            rng = np.random.default_rng(rng_seed)
            season_rows = run_experiment_for_input(
                input_path,
                season,
                run_args,
                rng,
                plot_sample=False,
            )
            for row in season_rows:
                row["scale_multiplier"] = multiplier
            rows.extend(season_rows)

    output_path = Path(args.output)
    summary_path = Path(args.summary_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    write_summaries(summary_path, summarize_rows(rows))
    print(f"Wrote: {output_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
