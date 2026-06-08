"""Compare simple reconstruction baselines for contiguous tracking gaps."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np

from geometry import (
    latlon_to_unit_sphere,
    normalize_vectors,
    resample_curve,
    spherical_linear_interpolate,
)
from missing_data_stability import (
    METRICS,
    compare_matrices,
    read_trajectory_points,
    select_trajectories,
    summarize_rows,
    write_summaries,
)
from evaluate_clusters import cluster_precomputed


def records_to_sphere(records):
    """Convert timestamped latitude-longitude records to unit-sphere points."""
    latitudes = [record[1] for record in records]
    longitudes = [record[2] for record in records]
    return latlon_to_unit_sphere(latitudes, longitudes)


def sphere_to_curve(points, n_points):
    """Resample unit-sphere points to the fixed curve representation."""
    return normalize_vectors(resample_curve(points, n_points))


def sample_gap_indices(n_records, missing_fraction, rng):
    """Sample a contiguous interior gap."""
    gap_size = min(n_records - 2, max(1, int(round(n_records * missing_fraction))))
    start = int(rng.integers(1, n_records - gap_size))
    stop = start + gap_size
    return start, stop


def observed_only_curve(records, start, stop, n_points):
    """Use only observed points after deleting a contiguous gap."""
    observed = records[:start] + records[stop:]
    return sphere_to_curve(records_to_sphere(observed), n_points)


def spherical_bridge_curve(records, start, stop, n_points):
    """Fill the deleted gap with great-circle interpolation before resampling."""
    points = records_to_sphere(records)
    gap_size = stop - start
    before = points[start - 1]
    after = points[stop]
    fractions = np.linspace(0.0, 1.0, gap_size + 2)[1:-1]
    bridge = spherical_linear_interpolate(before, after, fractions)
    reconstructed = np.vstack([points[:start], bridge, points[stop:]])
    return sphere_to_curve(reconstructed, n_points)


def write_rows(path, rows):
    """Write reconstruction-baseline diagnostics."""
    fieldnames = [
        "missing_fraction",
        "repeat",
        "reconstruction_method",
        "metric",
        "n_trajectories",
        "n_points",
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_reconstruction_rows(rows):
    """Summarize diagnostics by missing fraction, reconstruction method, and metric."""
    adapted = []
    for row in rows:
        adapted.append(
            {
                "missing_mechanism": row["reconstruction_method"],
                "missing_fraction": row["missing_fraction"],
                "metric": row["metric"],
                "matrix_spearman": row["matrix_spearman"],
                "median_relative_error": row["median_relative_error"],
                "cluster_ari": row["cluster_ari"],
                "anomaly_rank_spearman": row["anomaly_rank_spearman"],
                "top_k_overlap": row["top_k_overlap"],
            }
        )
    summaries = summarize_rows(adapted)
    for row in summaries:
        row["reconstruction_method"] = row.pop("missing_mechanism")
    return summaries


def write_reconstruction_summaries(path, rows):
    """Write summarized reconstruction diagnostics."""
    diagnostics = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    fieldnames = ["reconstruction_method", "missing_fraction", "metric", "n_repeats"]
    for diagnostic in diagnostics:
        fieldnames.extend([f"{diagnostic}_mean", f"{diagnostic}_std"])
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/gap_reconstruction_baseline.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="data/processed/gap_reconstruction_baseline_summary.csv",
    )
    parser.add_argument("--max-trajectories", type=int, default=30)
    parser.add_argument("--min-points", type=int, default=100)
    parser.add_argument("--n-points", type=int, default=60)
    parser.add_argument("--n-clusters", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--missing-fractions", nargs="+", type=float, default=[0.2, 0.4, 0.6])
    parser.add_argument("--seed", type=int, default=20260604)
    args = parser.parse_args()

    groups = read_trajectory_points(args.input)
    selected = select_trajectories(groups, args.min_points, args.max_trajectories)
    labels = [trajectory_id for trajectory_id, _ in selected]
    baseline_curves = [
        sphere_to_curve(records_to_sphere(records), args.n_points)
        for _, records in selected
    ]
    baseline_matrices = {
        metric: distance_function(baseline_curves)
        for metric, distance_function in METRICS.items()
    }
    baseline_clusters = {
        metric: cluster_precomputed(matrix, args.n_clusters)
        for metric, matrix in baseline_matrices.items()
    }

    methods = OrderedDict(
        [
            ("observed_only", observed_only_curve),
            ("spherical_bridge", spherical_bridge_curve),
        ]
    )
    rng = np.random.default_rng(args.seed)
    rows = []
    for missing_fraction in args.missing_fractions:
        for repeat in range(1, args.repeats + 1):
            gaps = [
                sample_gap_indices(len(records), missing_fraction, rng)
                for _, records in selected
            ]
            for method_name, curve_function in methods.items():
                curves = [
                    curve_function(records, start, stop, args.n_points)
                    for (_, records), (start, stop) in zip(selected, gaps)
                ]
                for metric, distance_function in METRICS.items():
                    matrix = distance_function(curves)
                    diagnostics = compare_matrices(
                        baseline_matrices[metric],
                        matrix,
                        baseline_clusters[metric],
                        args.n_clusters,
                        args.top_k,
                    )
                    rows.append(
                        {
                            "missing_fraction": missing_fraction,
                            "repeat": repeat,
                            "reconstruction_method": method_name,
                            "metric": metric,
                            "n_trajectories": len(labels),
                            "n_points": args.n_points,
                            **diagnostics,
                        }
                    )
            print(
                f"Completed gap reconstruction, missing={missing_fraction:.0%}, "
                f"repeat={repeat}/{args.repeats}"
            )

    output_path = Path(args.output)
    summary_path = Path(args.summary_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    write_reconstruction_summaries(summary_path, summarize_reconstruction_rows(rows))
    print(f"Processed {len(labels)} trajectories")
    print(f"Wrote: {output_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
