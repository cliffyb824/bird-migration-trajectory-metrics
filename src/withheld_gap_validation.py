"""Validate gap reconstructions against withheld observed route segments."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from brownian_bridge_gap_reconstruction import (
    brownian_bridge_sphere_sample,
    estimate_global_bridge_scale,
)
from gap_reconstruction_baseline import (
    records_to_sphere,
    sample_gap_indices,
)
from geometry import great_circle_distance_km, normalize_vectors, spherical_linear_interpolate
from missing_data_stability import read_trajectory_points, select_trajectories


def bridge_points(records, start, stop):
    """Return deterministic spherical-bridge points for the withheld interval."""
    points = records_to_sphere(records)
    gap_size = stop - start
    fractions = np.linspace(0.0, 1.0, gap_size + 2)[1:-1]
    return spherical_linear_interpolate(points[start - 1], points[stop], fractions)


def sample_center_and_radius(sample_points, quantile):
    """Estimate pointwise sample centers and uncertainty radii on the sphere."""
    samples = np.asarray(sample_points, dtype=float)
    centers = normalize_vectors(np.mean(samples, axis=0))
    sample_distances = great_circle_distance_km(samples, centers[None, :, :])
    radii = np.quantile(sample_distances, quantile, axis=0)
    return centers, radii


def validate_one_gap(records, start, stop, scale, n_samples, rng):
    """Compute withheld-segment validation diagnostics for one route gap."""
    true_points = records_to_sphere(records)[start:stop]
    deterministic = bridge_points(records, start, stop)
    deterministic_errors = great_circle_distance_km(deterministic, true_points)

    samples = [
        brownian_bridge_sphere_sample(records, start, stop, scale, rng)[start:stop]
        for _ in range(n_samples)
    ]
    sample_array = np.asarray(samples, dtype=float)
    sample_errors = great_circle_distance_km(sample_array, true_points[None, :, :])
    centers, radii_90 = sample_center_and_radius(sample_array, 0.90)
    center_errors = great_circle_distance_km(centers, true_points)
    ratios = center_errors / np.maximum(radii_90, 1e-9)
    radius_inflation_90 = float(np.quantile(ratios, 0.90))
    calibrated_radii_90 = radii_90 * radius_inflation_90

    return {
        "gap_points": stop - start,
        "deterministic_mean_error_km": float(np.mean(deterministic_errors)),
        "deterministic_median_error_km": float(np.median(deterministic_errors)),
        "sample_mean_error_km": float(np.mean(sample_errors)),
        "sample_median_error_km": float(np.median(sample_errors)),
        "sample_center_mean_error_km": float(np.mean(center_errors)),
        "oracle_sample_mean_error_km": float(np.mean(np.min(sample_errors, axis=0))),
        "coverage_90": float(np.mean(center_errors <= radii_90)),
        "radius_inflation_for_90_coverage": radius_inflation_90,
        "calibrated_coverage_90": float(np.mean(center_errors <= calibrated_radii_90)),
        "median_radius_90_km": float(np.median(radii_90)),
        "median_calibrated_radius_90_km": float(np.median(calibrated_radii_90)),
    }


def write_rows(path, rows):
    """Write per-gap withheld validation rows."""
    fieldnames = [
        "season",
        "missing_fraction",
        "repeat",
        "trajectory_id",
        "bridge_scale",
        "gap_points",
        "deterministic_mean_error_km",
        "deterministic_median_error_km",
        "sample_mean_error_km",
        "sample_median_error_km",
        "sample_center_mean_error_km",
        "oracle_sample_mean_error_km",
        "coverage_90",
        "radius_inflation_for_90_coverage",
        "calibrated_coverage_90",
        "median_radius_90_km",
        "median_calibrated_radius_90_km",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_rows(rows):
    """Summarize validation diagnostics by season and withheld fraction."""
    metrics = [
        "deterministic_mean_error_km",
        "sample_mean_error_km",
        "sample_center_mean_error_km",
        "oracle_sample_mean_error_km",
        "coverage_90",
        "radius_inflation_for_90_coverage",
        "calibrated_coverage_90",
        "median_radius_90_km",
        "median_calibrated_radius_90_km",
    ]
    grouped = {}
    for row in rows:
        key = (row["season"], row["missing_fraction"])
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (season, fraction), group in grouped.items():
        summary = {
            "season": season,
            "missing_fraction": fraction,
            "n_gaps": len(group),
            "bridge_scale": float(np.mean([row["bridge_scale"] for row in group])),
            "mean_gap_points": float(np.mean([row["gap_points"] for row in group])),
        }
        for metric in metrics:
            values = np.asarray([row[metric] for row in group], dtype=float)
            summary[f"{metric}_mean"] = float(np.mean(values))
            summary[f"{metric}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        summaries.append(summary)
    return summaries


def write_summaries(path, rows):
    """Write summarized withheld validation diagnostics."""
    fieldnames = [
        "season",
        "missing_fraction",
        "n_gaps",
        "bridge_scale",
        "mean_gap_points",
        "deterministic_mean_error_km_mean",
        "deterministic_mean_error_km_std",
        "sample_mean_error_km_mean",
        "sample_mean_error_km_std",
        "sample_center_mean_error_km_mean",
        "sample_center_mean_error_km_std",
        "oracle_sample_mean_error_km_mean",
        "oracle_sample_mean_error_km_std",
        "coverage_90_mean",
        "coverage_90_std",
        "radius_inflation_for_90_coverage_mean",
        "radius_inflation_for_90_coverage_std",
        "calibrated_coverage_90_mean",
        "calibrated_coverage_90_std",
        "median_radius_90_km_mean",
        "median_radius_90_km_std",
        "median_calibrated_radius_90_km_mean",
        "median_calibrated_radius_90_km_std",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_for_input(season, input_path, args, rng):
    """Run withheld validation for one seasonal trajectory table."""
    groups = read_trajectory_points(input_path)
    selected = select_trajectories(groups, args.min_points, args.max_trajectories)
    scale = estimate_global_bridge_scale(selected, max_span=args.scale_max_span)
    print(f"{season} validation bridge scale: {scale:.6g}")

    rows = []
    for missing_fraction in args.missing_fractions:
        for repeat in range(1, args.repeats + 1):
            for trajectory_id, records in selected:
                start, stop = sample_gap_indices(len(records), missing_fraction, rng)
                rows.append(
                    {
                        "season": season,
                        "missing_fraction": missing_fraction,
                        "repeat": repeat,
                        "trajectory_id": trajectory_id,
                        "bridge_scale": scale,
                        **validate_one_gap(
                            records,
                            start,
                            stop,
                            scale,
                            args.bridge_samples,
                            rng,
                        ),
                    }
                )
            print(
                f"Completed {season}, withheld={missing_fraction:.0%}, "
                f"repeat={repeat}/{args.repeats}"
            )
    return rows


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
        default="data/processed/withheld_gap_validation.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="data/processed/withheld_gap_validation_summary.csv",
    )
    parser.add_argument("--max-trajectories", type=int, default=30)
    parser.add_argument("--min-points", type=int, default=100)
    parser.add_argument("--missing-fractions", nargs="+", type=float, default=[0.2, 0.4, 0.6])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--bridge-samples", type=int, default=24)
    parser.add_argument("--scale-max-span", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260607)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    rows = []
    rows.extend(run_for_input("spring", args.spring_input, args, rng))
    rows.extend(run_for_input("autumn", args.autumn_input, args, rng))

    output_path = Path(args.output)
    summary_path = Path(args.summary_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    write_summaries(summary_path, summarize_rows(rows))
    print(f"Wrote: {output_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
