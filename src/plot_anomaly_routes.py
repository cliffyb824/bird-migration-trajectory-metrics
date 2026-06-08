"""Plot top anomaly route candidates."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from plot_route_map import DEFAULT_COASTLINE, add_coastline, route_bounds


ZEEBRUGGE_LAT = 51.34
ZEEBRUGGE_LON = 3.18


def read_top_scores(path, top_n):
    """Read top anomaly trajectory IDs."""
    ids = []
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            ids.append(row["trajectory_id"])
            if len(ids) >= top_n:
                break
    return ids


def read_segments(path, trajectory_ids):
    """Read points for selected trajectories."""
    keep = set(trajectory_ids)
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
    return {
        trajectory_id: sorted(points, key=lambda item: item[0])
        for trajectory_id, points in groups.items()
    }


def plot_routes(groups, ordered_ids, output_path, coastline_path=None):
    """Plot selected anomaly routes."""
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = plt.get_cmap("tab10")
    bounds = route_bounds(groups)
    coastline_added = add_coastline(ax, coastline_path, bounds)

    for i, trajectory_id in enumerate(ordered_ids):
        points = groups.get(trajectory_id)
        if not points:
            continue
        lat = [point[1] for point in points]
        lon = [point[2] for point in points]
        color = cmap(i % 10)
        ax.plot(
            lon,
            lat,
            color=color,
            linewidth=1.2,
            alpha=0.85,
            label=f"{i + 1}. {trajectory_id}",
            zorder=3,
        )
        ax.scatter(lon[0], lat[0], color=color, s=18, marker="o", zorder=4)
        ax.scatter(lon[-1], lat[-1], color=color, s=24, marker="x", zorder=4)

    ax.scatter(
        [ZEEBRUGGE_LON],
        [ZEEBRUGGE_LAT],
        marker="*",
        s=180,
        color="black",
        label="Colony",
        zorder=5,
    )

    min_lon, max_lon, min_lat, max_lat = bounds
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    ax.set_title("Top Candidate Anomalous Routes by SRVF-DTW Mean Distance")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.35, alpha=0.45)
    ax.legend(fontsize=6, frameon=False, loc="best")
    if coastline_added:
        ax.text(
            0.01,
            0.01,
            "Coastline: Natural Earth 1:110m",
            transform=ax.transAxes,
            fontsize=7,
            color="0.35",
            ha="left",
            va="bottom",
        )
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scores",
        default="data/processed/prototype_50_transit_distances/srvf_dtw_anomaly_scores.csv",
    )
    parser.add_argument(
        "--segments",
        default="data/processed/lbbg_zeebrugge_transit_segments.csv",
    )
    parser.add_argument("--output", default="figures/top_anomaly_transit_coastline.png")
    parser.add_argument("--coastline-shp", default=DEFAULT_COASTLINE)
    parser.add_argument("--top-n", type=int, default=6)
    args = parser.parse_args()

    top_ids = read_top_scores(args.scores, args.top_n)
    groups = read_segments(args.segments, top_ids)
    plot_routes(groups, top_ids, args.output, args.coastline_shp)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
