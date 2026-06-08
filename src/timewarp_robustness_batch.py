"""Batch time-warp robustness test across multiple trajectories."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np

from geometry import latlon_to_unit_sphere, normalize_vectors
from srvf import pointwise_l2_distance, raw_dtw_distance, srvf_distance, srvf_dtw_distance
from timewarp_robustness import sample_curve_by_warp


def read_trajectories(path, max_trajectories=20, min_points=500):
    """Read multiple trajectories with enough points from a segment CSV."""
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

    trajectories = []
    for trajectory_id, records in groups.items():
        if len(records) < min_points:
            continue
        records = sorted(records, key=lambda item: item[0])
        latitudes = [record[1] for record in records]
        longitudes = [record[2] for record in records]
        curve = latlon_to_unit_sphere(latitudes, longitudes)
        trajectories.append((trajectory_id, normalize_vectors(curve)))
        if len(trajectories) >= max_trajectories:
            break

    if not trajectories:
        raise ValueError("no trajectories met the minimum point requirement")
    return trajectories


def run_batch(trajectories, n_points, gammas):
    """Run time-warp test on multiple trajectories."""
    rows = []
    for trajectory_id, curve in trajectories:
        base = sample_curve_by_warp(curve, n_points, gamma=1.0)
        for gamma in gammas:
            warped = sample_curve_by_warp(curve, n_points, gamma)
            rows.append(
                {
                    "trajectory_id": trajectory_id,
                    "gamma": gamma,
                    "pointwise_l2": pointwise_l2_distance(base, warped),
                    "raw_dtw": raw_dtw_distance(base, warped),
                    "srvf": srvf_distance(base, warped),
                    "srvf_dtw": srvf_dtw_distance(base, warped),
                }
            )
    return rows


def summarize(rows):
    """Summarize robustness rows by gamma."""
    by_gamma = OrderedDict()
    for row in rows:
        by_gamma.setdefault(row["gamma"], []).append(row)

    summary = []
    for gamma, gamma_rows in by_gamma.items():
        out = {"gamma": gamma, "n_trajectories": len(gamma_rows)}
        for metric in ["pointwise_l2", "raw_dtw", "srvf", "srvf_dtw"]:
            values = np.asarray([row[metric] for row in gamma_rows], dtype=float)
            out[f"{metric}_mean"] = float(np.mean(values))
            out[f"{metric}_std"] = float(np.std(values, ddof=0))
        summary.append(out)
    return summary


def write_rows(path, rows):
    """Write detailed batch rows."""
    fieldnames = [
        "trajectory_id",
        "gamma",
        "pointwise_l2",
        "raw_dtw",
        "srvf",
        "srvf_dtw",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path, rows):
    """Write summary rows."""
    fieldnames = [
        "gamma",
        "n_trajectories",
        "pointwise_l2_mean",
        "pointwise_l2_std",
        "raw_dtw_mean",
        "raw_dtw_std",
        "srvf_mean",
        "srvf_std",
        "srvf_dtw_mean",
        "srvf_dtw_std",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_spring_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/timewarp_robustness_batch.csv",
    )
    parser.add_argument(
        "--summary",
        default="data/processed/timewarp_robustness_batch_summary.csv",
    )
    parser.add_argument("--n-points", type=int, default=100)
    parser.add_argument("--min-points", type=int, default=500)
    parser.add_argument("--max-trajectories", type=int, default=20)
    args = parser.parse_args()

    gammas = [0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5]
    trajectories = read_trajectories(
        args.input,
        max_trajectories=args.max_trajectories,
        min_points=args.min_points,
    )
    rows = run_batch(trajectories, args.n_points, gammas)
    summary = summarize(rows)

    write_rows(args.output, rows)
    write_summary(args.summary, summary)
    print(f"Trajectories: {len(trajectories)}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.summary}")


if __name__ == "__main__":
    main()
