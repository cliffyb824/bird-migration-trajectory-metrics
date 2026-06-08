"""Brownian-bridge prototype for movement-aware contiguous-gap reconstruction."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from evaluate_clusters import cluster_precomputed
from gap_reconstruction_baseline import (
    records_to_sphere,
    sample_gap_indices,
    sphere_to_curve,
    spherical_bridge_curve,
)
from geometry import normalize_vectors, spherical_linear_interpolate
from missing_data_stability import (
    METRICS,
    compare_matrices,
    read_trajectory_points,
    select_trajectories,
)
def tangent_basis(point):
    """Construct an arbitrary orthonormal tangent basis at a unit-sphere point."""
    p = normalize_vectors(np.asarray(point, dtype=float))
    reference = np.array([0.0, 0.0, 1.0])
    if abs(float(np.dot(p, reference))) > 0.95:
        reference = np.array([0.0, 1.0, 0.0])
    e1 = reference - np.dot(reference, p) * p
    e1 = normalize_vectors(e1)
    e2 = np.cross(p, e1)
    e2 = normalize_vectors(e2)
    return e1, e2


def brownian_bridge_offsets(n_points, scale, rng):
    """Draw two-dimensional Brownian bridge offsets with zero endpoints."""
    if n_points <= 0:
        return np.empty((0, 2), dtype=float)
    increments = rng.normal(0.0, scale, size=(n_points + 1, 2))
    path = np.vstack([np.zeros((1, 2)), np.cumsum(increments, axis=0)])
    time = np.linspace(0.0, 1.0, n_points + 2)[:, None]
    bridge = path - time * path[-1]
    return bridge[1:-1]


def brownian_bridge_sphere_sample(records, start, stop, scale, rng):
    """Fill a deleted gap with tangent-plane Brownian bridge perturbations."""
    points = records_to_sphere(records)
    gap_size = stop - start
    before = points[start - 1]
    after = points[stop]
    fractions = np.linspace(0.0, 1.0, gap_size + 2)[1:-1]
    bridge = spherical_linear_interpolate(before, after, fractions)
    offsets = brownian_bridge_offsets(gap_size, scale, rng)

    perturbed = []
    for point, offset in zip(bridge, offsets):
        e1, e2 = tangent_basis(point)
        perturbed.append(point + offset[0] * e1 + offset[1] * e2)
    perturbed = normalize_vectors(np.asarray(perturbed, dtype=float))
    return np.vstack([points[:start], perturbed, points[stop:]])


def tangent_coordinates(point, target):
    """Project target-point displacement onto a tangent basis at point."""
    e1, e2 = tangent_basis(point)
    displacement = np.asarray(target, dtype=float) - np.asarray(point, dtype=float)
    return np.array([np.dot(displacement, e1), np.dot(displacement, e2)], dtype=float)


def estimate_bridge_scale_from_records(records, max_span=6, min_offsets=20):
    """Estimate a Brownian bridge tangent-plane scale from observed track residuals.

    The estimator compares observed intermediate points with the great-circle
    bridge between surrounding observations. Offsets are divided by the
    Brownian-bridge variance factor sqrt(t(1-t)) so the resulting scale is
    approximately a per-gap-step tangent-plane standard deviation.
    """
    points = records_to_sphere(records)
    offsets = []
    for span in range(2, min(max_span, len(points) - 1) + 1):
        for start in range(0, len(points) - span):
            stop = start + span
            fractions = np.arange(1, span, dtype=float) / span
            expected = spherical_linear_interpolate(points[start], points[stop], fractions)
            for fraction, expected_point, observed_point in zip(
                fractions,
                expected,
                points[start + 1 : stop],
            ):
                variance_factor = np.sqrt(max(fraction * (1.0 - fraction), 1e-12))
                offsets.extend(tangent_coordinates(expected_point, observed_point) / variance_factor)

    if len(offsets) < min_offsets:
        return float("nan")
    arr = np.asarray(offsets, dtype=float)
    robust_sigma = 1.4826 * np.median(np.abs(arr - np.median(arr)))
    if robust_sigma <= 0:
        robust_sigma = float(np.std(arr, ddof=1))
    return float(robust_sigma)


def estimate_global_bridge_scale(selected, max_span=6):
    """Estimate one global Brownian bridge scale from selected trajectories."""
    scales = [
        estimate_bridge_scale_from_records(records, max_span=max_span)
        for _, records in selected
    ]
    finite = np.asarray([scale for scale in scales if np.isfinite(scale) and scale > 0], dtype=float)
    if len(finite) == 0:
        raise ValueError("could not estimate a positive Brownian bridge scale")
    return float(np.median(finite))


def write_rows(path, rows):
    """Write Brownian bridge reconstruction diagnostics."""
    fieldnames = [
        "season",
        "missing_fraction",
        "repeat",
        "method",
        "metric",
        "sample",
        "bridge_scale",
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


def plot_route_samples(records, start, stop, samples, output):
    """Plot one route and Brownian bridge samples in longitude-latitude space."""
    observed = records[:start] + records[stop:]
    all_lons = [record[2] for record in records]
    all_lats = [record[1] for record in records]
    obs_lons = [record[2] for record in observed]
    obs_lats = [record[1] for record in observed]
    gap_lons = [record[2] for record in records[start:stop]]
    gap_lats = [record[1] for record in records[start:stop]]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(all_lons, all_lats, color="#555555", linewidth=1.4, label="Complete route")
    ax.scatter(obs_lons, obs_lats, s=8, color="#0072B2", alpha=0.6, label="Observed")
    ax.scatter(gap_lons, gap_lats, s=10, color="#D55E00", alpha=0.8, label="Removed gap")

    for sample in samples:
        lon = np.rad2deg(np.arctan2(sample[:, 1], sample[:, 0]))
        lat = np.rad2deg(np.arcsin(np.clip(sample[:, 2], -1.0, 1.0)))
        ax.plot(lon, lat, color="#CC79A7", linewidth=0.8, alpha=0.28)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Brownian bridge route samples inside a contiguous gap")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_experiment_for_input(
    input_path,
    season,
    args,
    rng,
    plot_sample,
):
    """Run Brownian bridge diagnostics for one input trajectory table."""
    groups = read_trajectory_points(input_path)
    selected = select_trajectories(groups, args.min_points, args.max_trajectories)
    bridge_scale = (
        estimate_global_bridge_scale(selected, max_span=args.scale_max_span)
        if args.estimate_bridge_scale
        else args.bridge_scale
    )
    print(f"{season} Brownian bridge scale: {bridge_scale:.6g}")
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

    rows = []
    for missing_fraction in args.missing_fractions:
        for repeat in range(1, args.repeats + 1):
            gaps = [
                sample_gap_indices(len(records), missing_fraction, rng)
                for _, records in selected
            ]
            bridge_curves = [
                spherical_bridge_curve(records, start, stop, args.n_points)
                for (_, records), (start, stop) in zip(selected, gaps)
            ]
            for metric, distance_function in METRICS.items():
                matrix = distance_function(bridge_curves)
                rows.append(
                    {
                        "season": season,
                        "missing_fraction": missing_fraction,
                        "repeat": repeat,
                        "method": "spherical_bridge",
                        "metric": metric,
                        "sample": 0,
                        "bridge_scale": 0.0,
                        "n_trajectories": len(selected),
                        "n_points": args.n_points,
                        **compare_matrices(
                            baseline_matrices[metric],
                            matrix,
                            baseline_clusters[metric],
                            args.n_clusters,
                            args.top_k,
                        ),
                    }
                )

            samples_by_trajectory = []
            for (_, records), (start, stop) in zip(selected, gaps):
                samples = [
                    brownian_bridge_sphere_sample(records, start, stop, bridge_scale, rng)
                    for _ in range(args.bridge_samples)
                ]
                samples_by_trajectory.append(samples)

            if plot_sample:
                plot_route_samples(
                    selected[0][1],
                    gaps[0][0],
                    gaps[0][1],
                    samples_by_trajectory[0],
                    args.sample_plot,
                )
                plot_sample = False

            for sample_index in range(args.bridge_samples):
                curves = [
                    sphere_to_curve(samples[sample_index], args.n_points)
                    for samples in samples_by_trajectory
                ]
                for metric, distance_function in METRICS.items():
                    matrix = distance_function(curves)
                    rows.append(
                        {
                            "season": season,
                            "missing_fraction": missing_fraction,
                            "repeat": repeat,
                            "method": "brownian_bridge_sample",
                            "metric": metric,
                            "sample": sample_index + 1,
                            "bridge_scale": bridge_scale,
                            "n_trajectories": len(selected),
                            "n_points": args.n_points,
                            **compare_matrices(
                                baseline_matrices[metric],
                                matrix,
                                baseline_clusters[metric],
                                args.n_clusters,
                                args.top_k,
                            ),
                        }
                    )
            print(
                f"Completed {season}, missing={missing_fraction:.0%}, "
                f"repeat={repeat}/{args.repeats}"
            )
    return rows


def summarize_brownian_rows(rows):
    """Summarize Brownian bridge diagnostics by season, gap level, method, and metric."""
    diagnostic_names = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    grouped = {}
    for row in rows:
        key = (row["season"], row["missing_fraction"], row["method"], row["metric"])
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (season, fraction, method, metric), group in grouped.items():
        summary = {
            "season": season,
            "missing_fraction": fraction,
            "method": method,
            "metric": metric,
            "n_samples": len(group),
            "n_trajectories": group[0]["n_trajectories"],
            "bridge_scale": float(np.mean([row["bridge_scale"] for row in group])),
        }
        for name in diagnostic_names:
            values = np.asarray([row[name] for row in group], dtype=float)
            summary[f"{name}_mean"] = float(np.nanmean(values))
            summary[f"{name}_std"] = (
                float(np.nanstd(values, ddof=1)) if len(values) > 1 else 0.0
            )
            summary[f"{name}_p05"] = float(np.nanquantile(values, 0.05))
            summary[f"{name}_p95"] = float(np.nanquantile(values, 0.95))
        summaries.append(summary)
    return summaries


def write_brownian_summaries(path, rows):
    """Write summarized Brownian bridge diagnostics."""
    diagnostic_names = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    fieldnames = [
        "season",
        "missing_fraction",
        "method",
        "metric",
        "n_samples",
        "n_trajectories",
        "bridge_scale",
    ]
    for name in diagnostic_names:
        fieldnames.extend([f"{name}_mean", f"{name}_std", f"{name}_p05", f"{name}_p95"])
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--season", default="spring")
    parser.add_argument("--spring-input", default=None)
    parser.add_argument("--autumn-input", default=None)
    parser.add_argument(
        "--output",
        default="data/processed/brownian_bridge_gap_reconstruction.csv",
    )
    parser.add_argument(
        "--summary-output",
        default="data/processed/brownian_bridge_gap_reconstruction_summary.csv",
    )
    parser.add_argument(
        "--sample-plot",
        default="figures/brownian_bridge_gap_reconstruction_samples.png",
    )
    parser.add_argument("--max-trajectories", type=int, default=12)
    parser.add_argument("--min-points", type=int, default=100)
    parser.add_argument("--n-points", type=int, default=50)
    parser.add_argument("--n-clusters", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--missing-fraction", type=float, default=None)
    parser.add_argument("--missing-fractions", nargs="+", type=float, default=None)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--bridge-samples", type=int, default=8)
    parser.add_argument("--bridge-scale", type=float, default=0.002)
    parser.add_argument(
        "--estimate-bridge-scale",
        action="store_true",
        help="estimate bridge scale from observed local bridge residuals",
    )
    parser.add_argument("--scale-max-span", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260604)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    args.missing_fractions = (
        args.missing_fractions
        if args.missing_fractions is not None
        else [args.missing_fraction if args.missing_fraction is not None else 0.4]
    )
    input_specs = []
    if args.spring_input:
        input_specs.append(("spring", args.spring_input))
    if args.autumn_input:
        input_specs.append(("autumn", args.autumn_input))
    if not input_specs:
        default_input = args.input or "data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv"
        input_specs.append((args.season, default_input))

    rows = []
    plot_sample = True
    for season, input_path in input_specs:
        season_rows = run_experiment_for_input(
            input_path,
            season,
            args,
            rng,
            plot_sample=plot_sample,
        )
        rows.extend(season_rows)
        plot_sample = False

    output_path = Path(args.output)
    summary_path = Path(args.summary_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    write_brownian_summaries(summary_path, summarize_brownian_rows(rows))
    print(f"Wrote: {output_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {args.sample_plot}")


if __name__ == "__main__":
    main()
