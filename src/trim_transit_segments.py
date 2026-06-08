"""Trim broad seasonal candidate segments to likely transit portions.

This script refines the broad spring/autumn windows produced by
`segment_migration.py`. It uses distance from the Zeebrugge colony to keep a
more focused movement period:

- autumn: from initial departure away from the colony to near the maximum
  seasonal distance;
- spring: from leaving the distant wintering area to returning near the colony.

This is still heuristic, but it removes more residence-period movement than the
original broad calendar windows.
"""

from __future__ import annotations

import argparse
import csv
from collections import OrderedDict
from pathlib import Path


def read_segments(path):
    """Read candidate segment points grouped by trajectory ID."""
    groups = OrderedDict()
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        fieldnames = reader.fieldnames
        for row in reader:
            groups.setdefault(row["trajectory_id"], []).append(row)
    return fieldnames, groups


def distance(row):
    """Distance-from-colony value from a row."""
    return float(row["distance_from_colony_km"])


def trim_autumn(rows, depart_km=100.0, max_fraction=0.9):
    """Trim autumn route from departure to near maximum seasonal distance."""
    distances = [distance(row) for row in rows]
    max_distance = max(distances)
    start = next((i for i, d in enumerate(distances) if d >= depart_km), None)
    if start is None:
        return []

    target = max_distance * max_fraction
    end = next(
        (i for i in range(start, len(rows)) if distances[i] >= target),
        len(rows) - 1,
    )
    return rows[start : end + 1]


def trim_spring(rows, return_km=100.0, max_fraction=0.9):
    """Trim spring route from leaving distant area to return near colony."""
    distances = [distance(row) for row in rows]
    max_distance = max(distances)
    start_threshold = max_distance * max_fraction
    start = next((i for i, d in enumerate(distances) if d <= start_threshold), None)
    if start is None:
        start = 0

    end = next(
        (i for i in range(start, len(rows)) if distances[i] <= return_km),
        len(rows) - 1,
    )
    return rows[start : end + 1]


def renumber_points(rows):
    """Reset point_index after trimming."""
    out = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        new_row["point_index"] = str(i)
        out.append(new_row)
    return out


def trim_segments(groups, min_points=20, depart_km=100.0, return_km=100.0, max_fraction=0.9):
    """Trim all candidate segment groups."""
    trimmed = []
    summary = []
    for trajectory_id, rows in groups.items():
        rows = sorted(rows, key=lambda row: int(row["point_index"]))
        season = rows[0]["season"]
        if season == "autumn":
            kept = trim_autumn(rows, depart_km=depart_km, max_fraction=max_fraction)
        elif season == "spring":
            kept = trim_spring(rows, return_km=return_km, max_fraction=max_fraction)
        else:
            continue

        if len(kept) < min_points:
            continue

        kept = renumber_points(kept)
        trimmed.extend(kept)
        distances = [distance(row) for row in kept]
        summary.append(
            {
                "trajectory_id": trajectory_id,
                "individual_id": kept[0]["individual_id"],
                "year": kept[0]["year"],
                "season": season,
                "n_points": len(kept),
                "start_timestamp": kept[0]["timestamp"],
                "end_timestamp": kept[-1]["timestamp"],
                "min_distance_from_colony_km": f"{min(distances):.6f}",
                "max_distance_from_colony_km": f"{max(distances):.6f}",
            }
        )
    return trimmed, summary


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
        default="data/processed/lbbg_zeebrugge_candidate_segments.csv",
    )
    parser.add_argument(
        "--output",
        default="data/processed/lbbg_zeebrugge_transit_segments.csv",
    )
    parser.add_argument(
        "--summary",
        default="data/processed/lbbg_zeebrugge_transit_segments_summary.csv",
    )
    parser.add_argument("--min-points", type=int, default=20)
    parser.add_argument("--depart-km", type=float, default=100.0)
    parser.add_argument("--return-km", type=float, default=100.0)
    parser.add_argument("--max-fraction", type=float, default=0.9)
    args = parser.parse_args()

    fieldnames, groups = read_segments(args.input)
    rows, summary = trim_segments(
        groups,
        min_points=args.min_points,
        depart_km=args.depart_km,
        return_km=args.return_km,
        max_fraction=args.max_fraction,
    )
    write_csv(args.output, rows, fieldnames)
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
            "min_distance_from_colony_km",
            "max_distance_from_colony_km",
        ],
    )
    print(f"Transit segments: {len(summary)}")
    print(f"Transit points: {len(rows)}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.summary}")


if __name__ == "__main__":
    main()
