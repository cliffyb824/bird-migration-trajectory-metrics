"""Prototype distance-matrix pipeline for bird migration trajectories.

Expected input columns:
- individual_id
- timestamp
- latitude
- longitude

The script writes three CSV files:
- pointwise_l2_distances.csv
- raw_dtw_distances.csv
- srvf_distances.csv
- srvf_dtw_distances.csv
- distance_summary.csv

This script uses only the standard library plus NumPy.
"""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

import numpy as np

from geometry import latlon_to_unit_sphere, normalize_vectors, resample_curve
from srvf import (
    pairwise_pointwise_l2_distance,
    pairwise_raw_dtw_distance,
    pairwise_srvf_distance,
    pairwise_srvf_dtw_distance,
)


def read_standardized_csv(csv_path, id_column):
    """Read standardized trajectories grouped by individual."""
    groups = OrderedDict()
    with Path(csv_path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        required = {id_column, "timestamp", "latitude", "longitude"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns: {sorted(missing)}")

        for row in reader:
            group_id = row[id_column]
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(
                (
                    row["timestamp"],
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
            )
    return groups


def load_trajectories(
    csv_path,
    id_column="individual_id",
    n_points=100,
    max_individuals=None,
    min_points=20,
):
    """Load trajectories from a standardized CSV file."""
    groups = read_standardized_csv(csv_path, id_column=id_column)
    curves = []
    labels = []

    for group_id, records in groups.items():
        if len(records) < min_points:
            continue

        records = sorted(records, key=lambda item: item[0])
        latitudes = [record[1] for record in records]
        longitudes = [record[2] for record in records]
        sphere_points = latlon_to_unit_sphere(latitudes, longitudes)
        curve = resample_curve(sphere_points, n_points)
        curve = normalize_vectors(curve)

        curves.append(curve)
        labels.append(str(group_id))
        if max_individuals is not None and len(curves) >= max_individuals:
            break

    if len(curves) < 2:
        raise ValueError("at least two usable trajectories are required")
    return labels, curves


def save_distance_matrix(path, labels, matrix):
    """Save a labeled square distance matrix."""
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["individual_id", *labels])
        for label, row in zip(labels, matrix):
            writer.writerow([label, *[f"{value:.10g}" for value in row]])


def upper_triangle_mean(matrix):
    """Mean of the strict upper triangle of a square matrix."""
    indices = np.triu_indices(len(matrix), k=1)
    return float(np.mean(matrix[indices]))


def save_summary(path, n_trajectories, pointwise, raw_dtw, srvf, srvf_dtw):
    """Save a small distance summary table."""
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["metric", "n_trajectories", "mean_distance"])
        writer.writerow(["pointwise_l2", n_trajectories, upper_triangle_mean(pointwise)])
        writer.writerow(["raw_dtw", n_trajectories, upper_triangle_mean(raw_dtw)])
        writer.writerow(["srvf", n_trajectories, upper_triangle_mean(srvf)])
        writer.writerow(["srvf_dtw", n_trajectories, upper_triangle_mean(srvf_dtw)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="standardized trajectory CSV")
    parser.add_argument("--output-dir", required=True, help="directory for outputs")
    parser.add_argument("--id-column", default="individual_id")
    parser.add_argument("--n-points", type=int, default=100)
    parser.add_argument("--max-individuals", type=int, default=25)
    parser.add_argument("--min-points", type=int, default=20)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    labels, curves = load_trajectories(
        args.input,
        id_column=args.id_column,
        n_points=args.n_points,
        max_individuals=args.max_individuals,
        min_points=args.min_points,
    )

    pointwise = pairwise_pointwise_l2_distance(curves)
    raw_dtw = pairwise_raw_dtw_distance(curves)
    srvf = pairwise_srvf_distance(curves)
    srvf_dtw = pairwise_srvf_dtw_distance(curves)

    save_distance_matrix(output_dir / "pointwise_l2_distances.csv", labels, pointwise)
    save_distance_matrix(output_dir / "raw_dtw_distances.csv", labels, raw_dtw)
    save_distance_matrix(output_dir / "srvf_distances.csv", labels, srvf)
    save_distance_matrix(output_dir / "srvf_dtw_distances.csv", labels, srvf_dtw)
    save_summary(
        output_dir / "distance_summary.csv",
        len(curves),
        pointwise,
        raw_dtw,
        srvf,
        srvf_dtw,
    )

    print(f"Processed {len(curves)} trajectories")
    print(f"Wrote outputs to {output_dir}")


if __name__ == "__main__":
    main()
