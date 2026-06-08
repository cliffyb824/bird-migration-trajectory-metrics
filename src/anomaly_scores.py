"""Compute prototype route anomaly scores from a distance matrix."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


def read_distance_matrix(path):
    """Read a labeled square distance matrix."""
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.reader(source)
        header = next(reader)
        labels = header[1:]
        matrix = []
        for row in reader:
            matrix.append([float(value) for value in row[1:]])
    return labels, np.asarray(matrix, dtype=float)


def compute_scores(labels, matrix):
    """Compute anomaly scores as mean distance to all other trajectories."""
    if len(labels) != len(matrix):
        raise ValueError("labels and matrix size do not match")

    scores = []
    for i, label in enumerate(labels):
        distances = np.delete(matrix[i], i)
        scores.append(
            {
                "trajectory_id": label,
                "mean_distance": float(np.mean(distances)),
                "median_distance": float(np.median(distances)),
                "max_distance": float(np.max(distances)),
            }
        )
    scores.sort(key=lambda row: row["mean_distance"], reverse=True)
    return scores


def write_scores(path, rows):
    """Write anomaly scores."""
    fieldnames = [
        "rank",
        "trajectory_id",
        "mean_distance",
        "median_distance",
        "max_distance",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for rank, row in enumerate(rows, start=1):
            writer.writerow({"rank": rank, **row})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--distance-matrix",
        default="data/processed/prototype_50_transit_distances/srvf_dtw_distances.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/prototype_50_transit_distances/srvf_dtw_anomaly_scores.csv",
    )
    args = parser.parse_args()

    labels, matrix = read_distance_matrix(args.distance_matrix)
    scores = compute_scores(labels, matrix)
    write_scores(args.output, scores)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
