"""Create first-pass migration trajectory segments from standardized GPS data.

This is a deliberately simple heuristic for the first research prototype.

It splits records by:
- individual;
- calendar year;
- season window.

Then it keeps only segments that show enough long-distance movement away from
the Zeebrugge breeding colony area.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path


EARTH_RADIUS_KM = 6371.0088
ZEEBRUGGE_LAT = 51.34
ZEEBRUGGE_LON = 3.18


SEASONS = {
    "spring": {2, 3, 4, 5},
    "autumn": {7, 8, 9, 10, 11},
}


def parse_timestamp(value):
    """Parse an ISO timestamp ending in Z."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometers."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def season_for_month(month):
    """Return the season label for a month, or None."""
    for season, months in SEASONS.items():
        if month in months:
            return season
    return None


def read_grouped_records(input_path):
    """Read standardized records grouped by candidate segment key."""
    groups = defaultdict(list)
    with Path(input_path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            timestamp = parse_timestamp(row["timestamp"])
            season = season_for_month(timestamp.month)
            if season is None:
                continue

            individual_id = row["individual_id"]
            key = (individual_id, timestamp.year, season)
            latitude = float(row["latitude"])
            longitude = float(row["longitude"])
            groups[key].append(
                {
                    "timestamp": row["timestamp"],
                    "latitude": latitude,
                    "longitude": longitude,
                    "species": row.get("species", ""),
                    "distance_from_colony_km": haversine_km(
                        latitude,
                        longitude,
                        ZEEBRUGGE_LAT,
                        ZEEBRUGGE_LON,
                    ),
                }
            )
    return groups


def segment_records(
    groups,
    min_points=30,
    min_max_distance_km=300.0,
    min_displacement_km=150.0,
):
    """Filter grouped records into candidate migration segments."""
    kept = []
    summary = []
    for (individual_id, year, season), records in groups.items():
        records = sorted(records, key=lambda row: row["timestamp"])
        if len(records) < min_points:
            continue

        max_distance = max(row["distance_from_colony_km"] for row in records)
        start = records[0]
        end = records[-1]
        displacement = haversine_km(
            start["latitude"],
            start["longitude"],
            end["latitude"],
            end["longitude"],
        )

        if max_distance < min_max_distance_km:
            continue
        if displacement < min_displacement_km:
            continue

        trajectory_id = f"{individual_id}|{year}|{season}"
        for point_index, row in enumerate(records):
            kept.append(
                {
                    "trajectory_id": trajectory_id,
                    "individual_id": individual_id,
                    "year": year,
                    "season": season,
                    "point_index": point_index,
                    "timestamp": row["timestamp"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "species": row["species"],
                    "distance_from_colony_km": f"{row['distance_from_colony_km']:.6f}",
                }
            )

        summary.append(
            {
                "trajectory_id": trajectory_id,
                "individual_id": individual_id,
                "year": year,
                "season": season,
                "n_points": len(records),
                "start_timestamp": records[0]["timestamp"],
                "end_timestamp": records[-1]["timestamp"],
                "max_distance_from_colony_km": f"{max_distance:.6f}",
                "start_end_displacement_km": f"{displacement:.6f}",
            }
        )
    return kept, summary


def write_csv(path, rows, fieldnames):
    """Write rows to CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_standardized.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/lbbg_zeebrugge_candidate_segments.csv",
    )
    parser.add_argument(
        "--summary",
        default="data/processed/lbbg_zeebrugge_candidate_segments_summary.csv",
    )
    parser.add_argument("--min-points", type=int, default=30)
    parser.add_argument("--min-max-distance-km", type=float, default=300.0)
    parser.add_argument("--min-displacement-km", type=float, default=150.0)
    args = parser.parse_args()

    groups = read_grouped_records(args.input)
    rows, summary = segment_records(
        groups,
        min_points=args.min_points,
        min_max_distance_km=args.min_max_distance_km,
        min_displacement_km=args.min_displacement_km,
    )

    write_csv(
        args.output,
        rows,
        [
            "trajectory_id",
            "individual_id",
            "year",
            "season",
            "point_index",
            "timestamp",
            "latitude",
            "longitude",
            "species",
            "distance_from_colony_km",
        ],
    )
    write_csv(
        args.summary,
        summary,
        [
            "trajectory_id",
            "individual_id",
            "year",
            "season",
            "n_points",
            "start_timestamp",
            "end_timestamp",
            "max_distance_from_colony_km",
            "start_end_displacement_km",
        ],
    )
    print(f"Candidate segments: {len(summary)}")
    print(f"Segment points: {len(rows)}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.summary}")


if __name__ == "__main__":
    main()
