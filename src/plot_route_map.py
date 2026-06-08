"""Create route maps with an optional Natural Earth coastline layer."""

from __future__ import annotations

import argparse
import csv
import struct
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ZEEBRUGGE_LAT = 51.34
ZEEBRUGGE_LON = 3.18
DEFAULT_COASTLINE = (
    "data/external/naturalearth/ne_110m_coastline/ne_110m_coastline.shp"
)


def read_assignments(path):
    """Read trajectory cluster assignments if available."""
    assignments = {}
    if path is None or not Path(path).exists():
        return assignments
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        cluster_column = None
        for candidate in ["srvf_cluster", "cluster"]:
            if candidate in (reader.fieldnames or []):
                cluster_column = candidate
                break
        if cluster_column is None:
            return assignments
        for row in reader:
            assignments[row["trajectory_id"]] = int(row[cluster_column])
    return assignments


def read_segments(path, max_trajectories=None, assignments=None):
    """Read segment points grouped by trajectory."""
    groups = defaultdict(list)
    keep_ids = set(assignments) if assignments else None
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            trajectory_id = row["trajectory_id"]
            if keep_ids is not None and trajectory_id not in keep_ids:
                continue
            if max_trajectories is not None and len(groups) >= max_trajectories:
                if trajectory_id not in groups:
                    continue
            groups[trajectory_id].append(
                (
                    int(row["point_index"]),
                    float(row["latitude"]),
                    float(row["longitude"]),
                )
            )

    out = {}
    for trajectory_id, points in groups.items():
        out[trajectory_id] = sorted(points, key=lambda item: item[0])
    return out


def read_polyline_shapefile(path):
    """Read PolyLine records from a shapefile without external GIS packages."""
    path = Path(path)
    if not path.exists():
        return []

    lines = []
    with path.open("rb") as source:
        source.seek(100)
        while True:
            header = source.read(8)
            if len(header) < 8:
                break
            _, content_words = struct.unpack(">2i", header)
            content = source.read(content_words * 2)
            if len(content) < 44:
                continue

            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type == 0:
                continue
            if shape_type != 3:
                raise ValueError(f"Expected PolyLine shapefile, got shape type {shape_type}")

            num_parts, num_points = struct.unpack("<2i", content[36:44])
            parts_offset = 44
            points_offset = parts_offset + (num_parts * 4)
            parts = list(struct.unpack(f"<{num_parts}i", content[parts_offset:points_offset]))
            points = []
            for idx in range(num_points):
                offset = points_offset + (idx * 16)
                points.append(struct.unpack("<2d", content[offset : offset + 16]))

            part_starts = parts + [num_points]
            for start, end in zip(part_starts[:-1], part_starts[1:]):
                if end - start >= 2:
                    lines.append(points[start:end])
    return lines


def line_touches_bounds(line, bounds):
    """Return True if a line part overlaps the displayed lon-lat extent."""
    min_lon, max_lon, min_lat, max_lat = bounds
    lons = [point[0] for point in line]
    lats = [point[1] for point in line]
    return not (
        max(lons) < min_lon
        or min(lons) > max_lon
        or max(lats) < min_lat
        or min(lats) > max_lat
    )


def add_coastline(ax, coastline_path, bounds):
    """Draw Natural Earth coastline lines when the shapefile is available."""
    if coastline_path is None:
        return False
    lines = read_polyline_shapefile(coastline_path)
    if not lines:
        return False
    for line in lines:
        if not line_touches_bounds(line, bounds):
            continue
        lon = [point[0] for point in line]
        lat = [point[1] for point in line]
        ax.plot(lon, lat, color="0.35", linewidth=0.45, alpha=0.9, zorder=1)
    return True


def route_bounds(groups):
    """Compute padded lon-lat bounds from trajectory points."""
    all_lat = []
    all_lon = []
    for points in groups.values():
        all_lat.extend(point[1] for point in points)
        all_lon.extend(point[2] for point in points)

    if not all_lat or not all_lon:
        return (-10.0, 10.0, 45.0, 60.0)

    lon_pad = max(1.0, (max(all_lon) - min(all_lon)) * 0.08)
    lat_pad = max(1.0, (max(all_lat) - min(all_lat)) * 0.08)
    return (
        min(all_lon) - lon_pad,
        max(all_lon) + lon_pad,
        min(all_lat) - lat_pad,
        max(all_lat) + lat_pad,
    )


def plot_routes(groups, assignments, output_path, title, coastline_path=None):
    """Plot route trajectories with start/end and colony markers."""
    cmap = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(8, 8))
    bounds = route_bounds(groups)
    coastline_added = add_coastline(ax, coastline_path, bounds)

    for trajectory_id, points in groups.items():
        if len(points) < 2:
            continue
        lat = [point[1] for point in points]
        lon = [point[2] for point in points]
        cluster = assignments.get(trajectory_id, 1)
        color = cmap((cluster - 1) % 10)
        ax.plot(lon, lat, color=color, linewidth=0.8, alpha=0.65, zorder=3)
        ax.scatter(lon[0], lat[0], color=color, s=12, marker="o", alpha=0.9, zorder=4)
        ax.scatter(lon[-1], lat[-1], color=color, s=16, marker="x", alpha=0.9, zorder=4)

    ax.scatter(
        [ZEEBRUGGE_LON],
        [ZEEBRUGGE_LAT],
        marker="*",
        s=180,
        color="black",
        label="Approx. breeding colony",
        zorder=5,
    )

    min_lon, max_lon, min_lat, max_lat = bounds
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linewidth=0.35, alpha=0.45)

    if assignments:
        clusters = sorted(set(assignments.values()))
        handles = [
            plt.Line2D(
                [0],
                [0],
                color=cmap((cluster - 1) % 10),
                lw=2,
                label=f"Cluster {cluster}",
            )
            for cluster in clusters
        ]
        handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="*",
                color="black",
                linestyle="None",
                markersize=10,
                label="Colony",
            )
        )
        ax.legend(handles=handles, fontsize=8, frameon=False, loc="best")
    else:
        ax.legend(frameon=False, loc="best")

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
        "--segments",
        default="data/processed/lbbg_zeebrugge_candidate_segments.csv",
    )
    parser.add_argument(
        "--assignments",
        default="figures/prototype_50_segments/srvf_cluster_assignments.csv",
    )
    parser.add_argument("--output", default="figures/route_map_fallback.png")
    parser.add_argument("--coastline-shp", default=DEFAULT_COASTLINE)
    parser.add_argument("--max-trajectories", type=int, default=50)
    parser.add_argument(
        "--title",
        default="Candidate Migration Route Segments",
    )
    args = parser.parse_args()

    assignments = read_assignments(args.assignments)
    groups = read_segments(
        args.segments,
        max_trajectories=args.max_trajectories,
        assignments=assignments,
    )
    plot_routes(groups, assignments, args.output, args.title, args.coastline_shp)
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()
