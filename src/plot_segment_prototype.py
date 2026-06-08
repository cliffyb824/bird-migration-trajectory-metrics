"""Create first figures for segmented-route SRVF prototype."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform
from sklearn.cluster import AgglomerativeClustering


def read_distance_matrix(path):
    """Read a labeled square distance matrix written by prototype_distances.py."""
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.reader(source)
        header = next(reader)
        labels = header[1:]
        matrix = []
        for row in reader:
            matrix.append([float(value) for value in row[1:]])
    return labels, np.asarray(matrix, dtype=float)


def read_segment_points(path, keep_ids):
    """Read trajectory points for selected segment IDs."""
    keep = set(keep_ids)
    groups = defaultdict(list)
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            trajectory_id = row["trajectory_id"]
            if trajectory_id not in keep:
                continue
            groups[trajectory_id].append(
                (
                    int(row["point_index"]),
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
            )

    for trajectory_id in groups:
        groups[trajectory_id] = sorted(groups[trajectory_id], key=lambda item: item[0])
    return groups


def cluster_labels(distance_matrix, n_clusters):
    """Cluster a precomputed distance matrix."""
    kwargs = {
        "n_clusters": n_clusters,
        "linkage": "average",
    }
    try:
        model = AgglomerativeClustering(metric="precomputed", **kwargs)
    except TypeError:
        model = AgglomerativeClustering(affinity="precomputed", **kwargs)
    return model.fit_predict(distance_matrix)


def plot_heatmap(labels, matrix, output_path, title):
    """Plot a clustered heatmap for a distance matrix."""
    condensed = squareform(matrix, checks=False)
    order = leaves_list(linkage(condensed, method="average"))
    ordered = matrix[order][:, order]
    ordered_labels = [labels[i] for i in order]

    fig, ax = plt.subplots(figsize=(9, 8))
    image = ax.imshow(ordered, cmap="viridis")
    ax.set_title(title)
    ax.set_xlabel("Trajectory")
    ax.set_ylabel("Trajectory")
    ax.set_xticks(range(len(ordered_labels)))
    ax.set_yticks(range(len(ordered_labels)))
    ax.set_xticklabels(range(1, len(ordered_labels) + 1), fontsize=6)
    ax.set_yticklabels(range(1, len(ordered_labels) + 1), fontsize=6)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="Distance")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_routes(segment_points, labels, clusters, output_path):
    """Plot longitude-latitude tracks colored by cluster."""
    unique_clusters = sorted(set(clusters))
    cmap = plt.get_cmap("tab10")
    color_by_cluster = {
        cluster: cmap(i % 10) for i, cluster in enumerate(unique_clusters)
    }

    fig, ax = plt.subplots(figsize=(9, 7))
    for label, cluster in zip(labels, clusters):
        points = segment_points.get(label)
        if not points:
            continue
        lat = [point[1] for point in points]
        lon = [point[2] for point in points]
        ax.plot(
            lon,
            lat,
            color=color_by_cluster[cluster],
            linewidth=0.8,
            alpha=0.75,
        )
        ax.scatter(
            [lon[0]],
            [lat[0]],
            color=color_by_cluster[cluster],
            s=8,
            alpha=0.8,
        )

    ax.set_title("Candidate Migration Segments Colored by SRVF Cluster")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linewidth=0.3, alpha=0.4)
    handles = [
        plt.Line2D([0], [0], color=color_by_cluster[c], lw=2, label=f"Cluster {c + 1}")
        for c in unique_clusters
    ]
    ax.legend(handles=handles, fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def write_cluster_table(path, labels, clusters):
    """Write trajectory cluster assignments."""
    with Path(path).open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["trajectory_id", "cluster"])
        for label, cluster in zip(labels, clusters):
            writer.writerow([label, int(cluster) + 1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--distance-dir",
        default="data/processed/prototype_50_segment_distances",
    )
    parser.add_argument(
        "--segments",
        default="data/processed/lbbg_zeebrugge_candidate_segments.csv",
    )
    parser.add_argument("--output-dir", default="figures/prototype_50_segments")
    parser.add_argument("--n-clusters", type=int, default=4)
    args = parser.parse_args()

    distance_dir = Path(args.distance_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    point_labels, pointwise = read_distance_matrix(
        distance_dir / "pointwise_l2_distances.csv"
    )
    srvf_labels, srvf = read_distance_matrix(distance_dir / "srvf_distances.csv")
    if point_labels != srvf_labels:
        raise ValueError("distance matrices use different labels")

    clusters = cluster_labels(srvf, args.n_clusters)
    segment_points = read_segment_points(args.segments, srvf_labels)

    plot_heatmap(
        point_labels,
        pointwise,
        output_dir / "pointwise_l2_heatmap.png",
        "Pointwise L2 Distance Between Candidate Migration Segments",
    )
    plot_heatmap(
        srvf_labels,
        srvf,
        output_dir / "srvf_heatmap.png",
        "SRVF Distance Between Candidate Migration Segments",
    )
    plot_routes(
        segment_points,
        srvf_labels,
        clusters,
        output_dir / "srvf_clustered_routes.png",
    )
    write_cluster_table(output_dir / "srvf_cluster_assignments.csv", srvf_labels, clusters)

    print(f"Wrote figures and cluster assignments to {output_dir}")


if __name__ == "__main__":
    main()
