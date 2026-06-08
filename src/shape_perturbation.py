"""Controlled shape perturbation experiment for route-distance metrics."""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np

from geometry import latlon_to_unit_sphere, normalize_vectors
from srvf import pointwise_l2_distance, raw_dtw_distance, srvf_distance, srvf_dtw_distance
from timewarp_robustness import sample_curve_by_warp


def read_first_trajectory(path, min_points=500):
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


def moving_average_curve(curve, window=9):
    """Smooth a curve with a moving average and renormalize to the sphere."""
    arr = np.asarray(curve, dtype=float)
    if window < 3 or window % 2 == 0:
        raise ValueError("window must be an odd integer >= 3")
    pad = window // 2
    padded = np.pad(arr, ((pad, pad), (0, 0)), mode="edge")
    out = np.empty_like(arr)
    for i in range(len(arr)):
        out[i] = np.mean(padded[i : i + window], axis=0)
    return normalize_vectors(out)


def local_frame(point):
    """Construct two tangent directions at a unit-sphere point."""
    p = point / max(np.linalg.norm(point), 1e-12)
    reference = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(p, reference)) > 0.9:
        reference = np.array([1.0, 0.0, 0.0])
    u = np.cross(p, reference)
    u = u / max(np.linalg.norm(u), 1e-12)
    v = np.cross(p, u)
    v = v / max(np.linalg.norm(v), 1e-12)
    return u, v


def add_local_detour(curve, amplitude=0.08, center=0.5, width=0.16):
    """Push a middle section of the curve sideways in a tangent direction."""
    arr = np.asarray(curve, dtype=float).copy()
    n = len(arr)
    center_index = int(center * (n - 1))
    u, _ = local_frame(arr[center_index])
    t = np.linspace(0.0, 1.0, n)
    envelope = np.exp(-0.5 * ((t - center) / width) ** 2)
    out = arr + amplitude * envelope[:, None] * u[None, :]
    return normalize_vectors(out)


def add_local_loop(curve, amplitude=0.06, center=0.5, width=0.12):
    """Inject a small loop-like perturbation into the middle of the route."""
    arr = np.asarray(curve, dtype=float).copy()
    n = len(arr)
    center_index = int(center * (n - 1))
    u, v = local_frame(arr[center_index])
    t = np.linspace(0.0, 1.0, n)
    local = (t - center) / width
    envelope = np.exp(-0.5 * local**2)
    loop = (
        np.sin(2.0 * np.pi * local)[:, None] * u[None, :]
        + np.cos(2.0 * np.pi * local)[:, None] * v[None, :]
    )
    out = arr + amplitude * envelope[:, None] * loop
    return normalize_vectors(out)


def compare(base, variant):
    """Compute all distance metrics between a base curve and variant."""
    return {
        "pointwise_l2": pointwise_l2_distance(base, variant),
        "raw_dtw": raw_dtw_distance(base, variant),
        "srvf": srvf_distance(base, variant),
        "srvf_dtw": srvf_dtw_distance(base, variant),
    }


def run_experiment(curve, n_points=100):
    """Generate perturbations and compare distances."""
    base = sample_curve_by_warp(curve, n_points, gamma=1.0)
    variants = OrderedDict()
    variants["identity"] = base
    variants["time_warp_gamma_0.4"] = sample_curve_by_warp(curve, n_points, gamma=0.4)
    variants["time_warp_gamma_2.5"] = sample_curve_by_warp(curve, n_points, gamma=2.5)
    variants["smoothed"] = moving_average_curve(base, window=11)
    variants["local_detour"] = add_local_detour(base)
    variants["local_loop"] = add_local_loop(base)
    variants["reversed"] = base[::-1].copy()

    rows = []
    for name, variant in variants.items():
        distances = compare(base, variant)
        rows.append({"variant": name, **distances})
    return rows


def write_results(path, trajectory_id, rows):
    """Write experiment rows."""
    fieldnames = [
        "trajectory_id",
        "variant",
        "pointwise_l2",
        "raw_dtw",
        "srvf",
        "srvf_dtw",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
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
        default="data/processed/shape_perturbation.csv",
    )
    parser.add_argument("--n-points", type=int, default=100)
    parser.add_argument("--min-points", type=int, default=500)
    args = parser.parse_args()

    trajectory_id, curve = read_first_trajectory(args.input, min_points=args.min_points)
    rows = run_experiment(curve, n_points=args.n_points)
    write_results(args.output, trajectory_id, rows)
    print(f"Trajectory: {trajectory_id}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
