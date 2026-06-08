"""Controlled time-warp robustness test for trajectory distances."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np

from geometry import latlon_to_unit_sphere, normalize_vectors
from srvf import pointwise_l2_distance, raw_dtw_distance, srvf_distance, srvf_dtw_distance


def read_first_trajectory(path, min_points=100):
    """Read the first trajectory with enough points from a segment CSV."""
    groups = OrderedDict()
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            trajectory_id = row["trajectory_id"]
            groups.setdefault(trajectory_id, []).append(
                (
                    int(row["point_index"]),
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
            )

    for trajectory_id, records in groups.items():
        if len(records) >= min_points:
            records = sorted(records, key=lambda item: item[0])
            latitudes = [record[1] for record in records]
            longitudes = [record[2] for record in records]
            curve = latlon_to_unit_sphere(latitudes, longitudes)
            return trajectory_id, normalize_vectors(curve)

    raise ValueError("no trajectory has enough points")


def sample_curve_by_warp(curve, n_points, gamma):
    """Sample a curve under a monotone time warp t -> t**gamma."""
    arr = np.asarray(curve, dtype=float)
    original_t = np.linspace(0.0, 1.0, len(arr))
    warped_t = np.linspace(0.0, 1.0, n_points) ** gamma

    out = np.empty((n_points, arr.shape[1]), dtype=float)
    for dim in range(arr.shape[1]):
        out[:, dim] = np.interp(warped_t, original_t, arr[:, dim])
    return normalize_vectors(out)


def run_test(curve, n_points, gammas):
    """Compare original resampled curve to time-warped versions."""
    base = sample_curve_by_warp(curve, n_points, gamma=1.0)

    rows = []
    for gamma in gammas:
        warped = sample_curve_by_warp(curve, n_points, gamma)
        rows.append(
            {
                "gamma": gamma,
                "pointwise_l2": pointwise_l2_distance(base, warped),
                "raw_dtw": raw_dtw_distance(base, warped),
                "srvf": srvf_distance(base, warped),
                "srvf_dtw": srvf_dtw_distance(base, warped),
            }
        )
    return rows


def write_results(path, trajectory_id, rows):
    """Write robustness results."""
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=[
                "trajectory_id",
                "gamma",
                "pointwise_l2",
                "raw_dtw",
                "srvf",
                "srvf_dtw",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({"trajectory_id": trajectory_id, **row})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_spring_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/timewarp_robustness.csv",
    )
    parser.add_argument("--n-points", type=int, default=100)
    parser.add_argument("--min-points", type=int, default=500)
    args = parser.parse_args()

    trajectory_id, curve = read_first_trajectory(args.input, min_points=args.min_points)
    gammas = [0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5]
    rows = run_test(curve, args.n_points, gammas)
    write_results(args.output, trajectory_id, rows)
    print(f"Trajectory: {trajectory_id}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
