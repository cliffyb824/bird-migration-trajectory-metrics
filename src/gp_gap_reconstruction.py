"""Gaussian-process prototype for uncertainty-aware contiguous-gap reconstruction."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel

from evaluate_clusters import cluster_precomputed
from gap_reconstruction_baseline import (
    records_to_sphere,
    sample_gap_indices,
    sphere_to_curve,
    spherical_bridge_curve,
    write_reconstruction_summaries,
)
from missing_data_stability import (
    METRICS,
    compare_matrices,
    read_trajectory_points,
    select_trajectories,
    summarize_rows,
)


def normalized_time(n_points):
    """Return normalized time coordinates for one trajectory."""
    return np.linspace(0.0, 1.0, n_points)


def fit_dimension_gp(time_observed, values, length_scale, noise, amplitude):
    """Fit one fixed-hyperparameter GP for a coordinate dimension."""
    kernel = (
        ConstantKernel(amplitude, constant_value_bounds="fixed")
        * RBF(length_scale=length_scale, length_scale_bounds="fixed")
        + WhiteKernel(noise_level=noise, noise_level_bounds="fixed")
    )
    model = GaussianProcessRegressor(
        kernel=kernel,
        alpha=0.0,
        optimizer=None,
        normalize_y=True,
        random_state=0,
    )
    model.fit(time_observed[:, None], values)
    return model


def gp_reconstruct_sphere_samples(
    records,
    start,
    stop,
    n_samples,
    rng,
    length_scale,
    noise,
    amplitude,
):
    """Draw posterior sphere-coordinate route samples from independent GPs."""
    points = records_to_sphere(records)
    time_all = normalized_time(len(points))
    observed_mask = np.ones(len(points), dtype=bool)
    observed_mask[start:stop] = False
    time_observed = time_all[observed_mask]
    samples_by_dim = []
    for dim in range(points.shape[1]):
        model = fit_dimension_gp(
            time_observed,
            points[observed_mask, dim],
            length_scale=length_scale,
            noise=noise,
            amplitude=amplitude,
        )
        dim_samples = model.sample_y(
            time_all[:, None],
            n_samples=n_samples,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        samples_by_dim.append(dim_samples.T)

    samples = []
    for sample_index in range(n_samples):
        reconstructed = np.column_stack(
            [samples_by_dim[dim][sample_index] for dim in range(points.shape[1])]
        )
        reconstructed[observed_mask] = points[observed_mask]
        samples.append(reconstructed)
    return samples


def interval_width(values):
    """Return the 90% interval width for a one-dimensional array."""
    values = np.asarray(values, dtype=float)
    return float(np.quantile(values, 0.95) - np.quantile(values, 0.05))


def write_rows(path, rows):
    """Write GP reconstruction diagnostics."""
    fieldnames = [
        "missing_fraction",
        "repeat",
        "method",
        "metric",
        "sample",
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


def summarize_gp_rows(rows):
    """Summarize deterministic and GP posterior-sample diagnostics."""
    diagnostic_names = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    grouped = {}
    for row in rows:
        key = (row["missing_fraction"], row["method"], row["metric"])
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (fraction, method, metric), group in grouped.items():
        summary = {
            "missing_fraction": fraction,
            "method": method,
            "metric": metric,
            "n_samples": len(group),
        }
        for name in diagnostic_names:
            values = np.asarray([row[name] for row in group], dtype=float)
            summary[f"{name}_mean"] = float(np.nanmean(values))
            summary[f"{name}_std"] = (
                float(np.nanstd(values, ddof=1)) if len(values) > 1 else 0.0
            )
            summary[f"{name}_p05"] = float(np.nanquantile(values, 0.05))
            summary[f"{name}_p95"] = float(np.nanquantile(values, 0.95))
            summary[f"{name}_interval_width"] = interval_width(values)
        summaries.append(summary)
    return summaries


def write_summaries(path, rows):
    """Write summarized GP reconstruction diagnostics."""
    diagnostic_names = [
        "matrix_spearman",
        "median_relative_error",
        "cluster_ari",
        "anomaly_rank_spearman",
        "top_k_overlap",
    ]
    fieldnames = ["missing_fraction", "method", "metric", "n_samples"]
    for name in diagnostic_names:
        fieldnames.extend(
            [
                f"{name}_mean",
                f"{name}_std",
                f"{name}_p05",
                f"{name}_p95",
                f"{name}_interval_width",
            ]
        )
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_route_samples(records, start, stop, gp_samples, output):
    """Plot one latitude-longitude route with GP posterior gap samples."""
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

    for sample in gp_samples:
        lon = np.rad2deg(np.arctan2(sample[:, 1], sample[:, 0]))
        lat = np.rad2deg(np.arcsin(np.clip(sample[:, 2], -1.0, 1.0)))
        ax.plot(lon, lat, color="#009E73", linewidth=0.7, alpha=0.25)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("GP posterior route samples inside a contiguous gap")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_transit_spring_candidate_segments.csv",
    )
    parser.add_argument("--output", default="data/processed/gp_gap_reconstruction.csv")
    parser.add_argument(
        "--summary-output",
        default="data/processed/gp_gap_reconstruction_summary.csv",
    )
    parser.add_argument(
        "--sample-plot",
        default="figures/gp_gap_reconstruction_samples.png",
    )
    parser.add_argument("--max-trajectories", type=int, default=12)
    parser.add_argument("--min-points", type=int, default=100)
    parser.add_argument("--n-points", type=int, default=50)
    parser.add_argument("--n-clusters", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--missing-fraction", type=float, default=0.4)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--gp-samples", type=int, default=8)
    parser.add_argument("--length-scale", type=float, default=0.18)
    parser.add_argument("--noise", type=float, default=1e-4)
    parser.add_argument("--amplitude", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=20260604)
    args = parser.parse_args()

    groups = read_trajectory_points(args.input)
    selected = select_trajectories(groups, args.min_points, args.max_trajectories)
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

    rng = np.random.default_rng(args.seed)
    rows = []
    for repeat in range(1, args.repeats + 1):
        gaps = [
            sample_gap_indices(len(records), args.missing_fraction, rng)
            for _, records in selected
        ]
        bridge_curves = [
            spherical_bridge_curve(records, start, stop, args.n_points)
            for (_, records), (start, stop) in zip(selected, gaps)
        ]
        for metric, distance_function in METRICS.items():
            bridge_matrix = distance_function(bridge_curves)
            rows.append(
                {
                    "missing_fraction": args.missing_fraction,
                    "repeat": repeat,
                    "method": "spherical_bridge",
                    "metric": metric,
                    "sample": 0,
                    "n_trajectories": len(selected),
                    "n_points": args.n_points,
                    **compare_matrices(
                        baseline_matrices[metric],
                        bridge_matrix,
                        baseline_clusters[metric],
                        args.n_clusters,
                        args.top_k,
                    ),
                }
            )

        gp_samples_by_trajectory = [
            gp_reconstruct_sphere_samples(
                records,
                start,
                stop,
                args.gp_samples,
                rng,
                args.length_scale,
                args.noise,
                args.amplitude,
            )
            for (_, records), (start, stop) in zip(selected, gaps)
        ]
        if repeat == 1:
            plot_route_samples(
                selected[0][1],
                gaps[0][0],
                gaps[0][1],
                gp_samples_by_trajectory[0],
                args.sample_plot,
            )

        for sample_index in range(args.gp_samples):
            curves = [
                sphere_to_curve(samples[sample_index], args.n_points)
                for samples in gp_samples_by_trajectory
            ]
            for metric, distance_function in METRICS.items():
                matrix = distance_function(curves)
                rows.append(
                    {
                        "missing_fraction": args.missing_fraction,
                        "repeat": repeat,
                        "method": "gp_sample",
                        "metric": metric,
                        "sample": sample_index + 1,
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
        print(f"Completed GP gap reconstruction repeat {repeat}/{args.repeats}")

    output_path = Path(args.output)
    summary_path = Path(args.summary_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    write_summaries(summary_path, summarize_gp_rows(rows))
    print(f"Processed {len(selected)} trajectories")
    print(f"Wrote: {output_path}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {args.sample_plot}")


if __name__ == "__main__":
    main()
