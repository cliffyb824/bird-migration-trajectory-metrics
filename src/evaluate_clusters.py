"""Evaluate distance-matrix clustering quality for prototype experiments."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import davies_bouldin_score, silhouette_score


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


def cluster_precomputed(matrix, n_clusters):
    """Cluster a precomputed distance matrix."""
    kwargs = {
        "n_clusters": n_clusters,
        "linkage": "average",
    }
    try:
        model = AgglomerativeClustering(metric="precomputed", **kwargs)
    except TypeError:
        model = AgglomerativeClustering(affinity="precomputed", **kwargs)
    return model.fit_predict(matrix)


def cluster_sizes(labels):
    """Return cluster sizes as a compact string."""
    unique, counts = np.unique(labels, return_counts=True)
    return "; ".join(f"{int(cluster) + 1}:{int(count)}" for cluster, count in zip(unique, counts))


def evaluate_distance_matrix(name, labels, matrix, n_clusters):
    """Compute clustering metrics for a distance matrix."""
    assignments = cluster_precomputed(matrix, n_clusters)
    silhouette = silhouette_score(matrix, assignments, metric="precomputed")

    # Davies-Bouldin expects feature vectors, not distances. Classical MDS would
    # be cleaner, but using the distance rows as embeddings is a reasonable
    # prototype diagnostic.
    db_index = davies_bouldin_score(matrix, assignments)

    return {
        "metric": name,
        "n_trajectories": len(labels),
        "n_clusters": n_clusters,
        "silhouette_score": silhouette,
        "davies_bouldin_index": db_index,
        "cluster_sizes": cluster_sizes(assignments),
    }, assignments


def write_summary(path, rows):
    """Write metric summary rows."""
    fieldnames = [
        "metric",
        "n_trajectories",
        "n_clusters",
        "silhouette_score",
        "davies_bouldin_index",
        "cluster_sizes",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_assignments(path, labels, assignments_by_metric):
    """Write per-trajectory assignments for all metrics."""
    fieldnames = ["trajectory_id", *[f"{name}_cluster" for name in assignments_by_metric]]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        for i, label in enumerate(labels):
            row = {"trajectory_id": label}
            for name, assignments in assignments_by_metric.items():
                row[f"{name}_cluster"] = int(assignments[i]) + 1
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--distance-dir",
        default="data/processed/prototype_50_segment_distances",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed/prototype_50_segment_distances",
    )
    parser.add_argument("--n-clusters", type=int, default=4)
    args = parser.parse_args()

    distance_dir = Path(args.distance_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    matrices = []
    point_labels, pointwise = read_distance_matrix(
        distance_dir / "pointwise_l2_distances.csv"
    )
    matrices.append(("pointwise_l2", pointwise))

    raw_dtw_path = distance_dir / "raw_dtw_distances.csv"
    if raw_dtw_path.exists():
        raw_dtw_labels, raw_dtw = read_distance_matrix(raw_dtw_path)
        if point_labels != raw_dtw_labels:
            raise ValueError("distance matrices use different labels")
        matrices.append(("raw_dtw", raw_dtw))

    srvf_labels, srvf = read_distance_matrix(distance_dir / "srvf_distances.csv")
    if point_labels != srvf_labels:
        raise ValueError("distance matrices use different labels")
    matrices.append(("srvf", srvf))

    srvf_dtw_path = distance_dir / "srvf_dtw_distances.csv"
    if srvf_dtw_path.exists():
        srvf_dtw_labels, srvf_dtw = read_distance_matrix(srvf_dtw_path)
        if point_labels != srvf_dtw_labels:
            raise ValueError("distance matrices use different labels")
        matrices.append(("srvf_dtw", srvf_dtw))

    rows = []
    assignments_by_metric = {}
    for name, matrix in matrices:
        row, assignments = evaluate_distance_matrix(
            name,
            point_labels,
            matrix,
            args.n_clusters,
        )
        rows.append(row)
        assignments_by_metric[name] = assignments

    write_summary(output_dir / "cluster_evaluation.csv", rows)
    write_assignments(
        output_dir / "cluster_assignments_comparison.csv",
        point_labels,
        assignments_by_metric,
    )
    print(f"Wrote cluster evaluation to {output_dir}")


if __name__ == "__main__":
    main()
