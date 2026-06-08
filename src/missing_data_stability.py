"""Evaluate trajectory-metric stability under missing tracking observations."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np
from sklearn.metrics import adjusted_rand_score

from evaluate_clusters import cluster_precomputed
from geometry import latlon_to_unit_sphere, normalize_vectors, resample_curve
from srvf import pairwise_raw_dtw_distance, pairwise_srvf_dtw_distance


METRICS = {
    "raw_dtw": pairwise_raw_dtw_distance,
    "srvf_dtw": pairwise_srvf_dtw_distance,
}


def read_trajectory_points(path):
    """Read latitude-longitude points grouped by trajectory ID."""
    groups = OrderedDict()
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        required = {"trajectory_id", "timestamp", "latitude", "longitude"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns: {sorted(missing)}")
        for row in reader:
            groups.setdefault(row["trajectory_id"], []).append(
                (
                    row["timestamp"],
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
            )
    return groups


def select_trajectories(groups, min_points, max_trajectories):
    """Select trajectories with enough observations in deterministic order."""
    selected = []
    for trajectory_id, records in groups.items():
        records = sorted(records, key=lambda item: item[0])
        if len(records) < min_points:
            continue
        selected.append((trajectory_id, records))
        if len(selected) >= max_trajectories:
            break
    if len(selected) < 2:
        raise ValueError("at least two usable trajectories are required")
    return selected


def records_to_curve(records, n_points):
    """Convert timestamped latitude-longitude records to a resampled sphere curve."""
    latitudes = [record[1] for record in records]
    longitudes = [record[2] for record in records]
    sphere_points = latlon_to_unit_sphere(latitudes, longitudes)
    return normalize_vectors(resample_curve(sphere_points, n_points))


def remove_random_points(records, missing_fraction, rng):
    """Remove random interior observations while preserving route endpoints."""
    n = len(records)
    keep_count = max(2, int(round(n * (1.0 - missing_fraction))))
    interior = np.arange(1, n - 1)
    interior_keep = max(0, keep_count - 2)
    chosen = rng.choice(interior, size=interior_keep, replace=False)
    indices = np.sort(np.concatenate(([0], chosen, [n - 1])))
    return [records[int(index)] for index in indices]


def remove_contiguous_gap(records, missing_fraction, rng):
    """Remove one contiguous interior observation block while preserving endpoints."""
    n = len(records)
    gap_size = min(n - 2, max(1, int(round(n * missing_fraction))))
    start = int(rng.integers(1, n - gap_size))
    stop = start + gap_size
    return records[:start] + records[stop:]


def upper_triangle(matrix):
    """Return the strict upper triangle of a square matrix."""
    return np.asarray(matrix)[np.triu_indices(len(matrix), k=1)]


def rank_values(values):
    """Return average ranks for a one-dimensional array."""
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and sorted_values[stop] == sorted_values[start]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1)
        start = stop
    return ranks


def spearman_correlation(values_a, values_b):
    """Compute Spearman rank correlation without an external statistics dependency."""
    ranks_a = rank_values(values_a)
    ranks_b = rank_values(values_b)
    if np.std(ranks_a) == 0 or np.std(ranks_b) == 0:
        return float("nan")
    return float(np.corrcoef(ranks_a, ranks_b)[0, 1])


def anomaly_scores(matrix):
    """Compute mean distance to all other trajectories."""
    n = len(matrix)
    return np.asarray(
        [np.mean(np.delete(matrix[index], index)) for index in range(n)],
        dtype=float,
    )


def top_k_indices(values, k):
    """Return indices of the largest values."""
    return set(np.argsort(values)[-k:])


def compare_matrices(baseline, perturbed, baseline_clusters, n_clusters, top_k):
    """Compute stability diagnostics for one perturbed distance matrix."""
    baseline_upper = upper_triangle(baseline)
    perturbed_upper = upper_triangle(perturbed)
    positive = baseline_upper > 1e-12
    relative_error = np.abs(perturbed_upper[positive] - baseline_upper[positive]) / baseline_upper[
        positive
    ]

    perturbed_clusters = cluster_precomputed(perturbed, n_clusters)
    baseline_anomaly = anomaly_scores(baseline)
    perturbed_anomaly = anomaly_scores(perturbed)
    baseline_top = top_k_indices(baseline_anomaly, top_k)
    perturbed_top = top_k_indices(perturbed_anomaly, top_k)

    return {
        "matrix_spearman": spearman_correlation(baseline_upper, perturbed_upper),
        "median_relative_error": float(np.median(relative_error)),
        "cluster_ari": float(adjusted_rand_score(baseline_clusters, perturbed_clusters)),
        "anomaly_rank_spearman": spearman_correlation(baseline_anomaly, perturbed_anomaly),
        "top_k_overlap": len(baseline_top.intersection(perturbed_top)) / top_k,
    }


def write_rows(path, rows):
    """Write trajectory-metric stability results."""
    fieldnames = [
        "missing_mechanism",
        "missing_fraction",
        "repeat",
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


def summarize_rows(rows):
    """Summarize repeated stability diagnostics."""
    diagnostics = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    grouped = OrderedDict()
    for row in rows:
        key = (row["missing_mechanism"], row["missing_fraction"], row["metric"])
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (mechanism, fraction, metric), group in grouped.items():
        summary = {
            "missing_mechanism": mechanism,
            "missing_fraction": fraction,
            "metric": metric,
            "n_repeats": len(group),
        }
        for diagnostic in diagnostics:
            values = np.asarray([row[diagnostic] for row in group], dtype=float)
            summary[f"{diagnostic}_mean"] = float(np.nanmean(values))
            summary[f"{diagnostic}_std"] = (
                float(np.nanstd(values, ddof=1)) if len(values) > 1 else 0.0
            )
        summaries.append(summary)
    return summaries


def write_summaries(path, rows):
    """Write summarized stability diagnostics."""
    diagnostics = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    fieldnames = ["missing_mechanism", "missing_fraction", "metric", "n_repeats"]
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
        default="data/processed/missing_data_stability.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="data/processed/missing_data_stability_summary.csv",
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
    baseline_curves = [records_to_curve(records, args.n_points) for _, records in selected]

    baseline_matrices = {
        metric: distance_function(baseline_curves)
        for metric, distance_function in METRICS.items()
    }
    baseline_clusters = {
        metric: cluster_precomputed(matrix, args.n_clusters)
        for metric, matrix in baseline_matrices.items()
    }

    rng = np.random.default_rng(args.seed)
    mechanisms = {
        "random_points": remove_random_points,
        "contiguous_gap": remove_contiguous_gap,
    }
    rows = []
    for mechanism_name, removal_function in mechanisms.items():
        for missing_fraction in args.missing_fractions:
            for repeat in range(1, args.repeats + 1):
                perturbed_curves = [
                    records_to_curve(removal_function(records, missing_fraction, rng), args.n_points)
                    for _, records in selected
                ]
                for metric, distance_function in METRICS.items():
                    perturbed_matrix = distance_function(perturbed_curves)
                    diagnostics = compare_matrices(
                        baseline_matrices[metric],
                        perturbed_matrix,
                        baseline_clusters[metric],
                        args.n_clusters,
                        args.top_k,
                    )
                    rows.append(
                        {
                            "missing_mechanism": mechanism_name,
                            "missing_fraction": missing_fraction,
                            "repeat": repeat,
                            "metric": metric,
                            "n_trajectories": len(labels),
                            "n_points": args.n_points,
                            **diagnostics,
                        }
                    )
                print(
                    f"Completed {mechanism_name}, missing={missing_fraction:.0%}, "
                    f"repeat={repeat}/{args.repeats}"
                )

    output_path = Path(args.output)
    summary_path = Path(args.summary_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    write_summaries(summary_path, summarize_rows(rows))
    print(f"Processed {len(labels)} trajectories")
    print(f"Wrote: {output_path}")
    print(f"Wrote: {summary_path}")


if __name__ == "__main__":
    main()
