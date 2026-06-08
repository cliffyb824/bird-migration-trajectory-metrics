"""Summarize sensitivity of transit-route counts to trimming thresholds."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from trim_transit_segments import read_segments, trim_segments


def summarize(rows):
    """Summarize trimmed rows by season."""
    route_ids = {}
    point_counts = {}
    individuals = {}
    for row in rows:
        season = row["season"]
        route_ids.setdefault(season, set()).add(row["trajectory_id"])
        point_counts[season] = point_counts.get(season, 0) + 1
        individuals.setdefault(season, set()).add(row["individual_id"])

    out = []
    for season in ["spring", "autumn"]:
        out.append(
            {
                "season": season,
                "transit_routes": len(route_ids.get(season, set())),
                "individuals": len(individuals.get(season, set())),
                "transit_points": point_counts.get(season, 0),
            }
        )
    out.append(
        {
            "season": "total",
            "transit_routes": sum(len(values) for values in route_ids.values()),
            "individuals": len(set().union(*individuals.values())) if individuals else 0,
            "transit_points": sum(point_counts.values()),
        }
    )
    return out


def write_rows(path, rows):
    """Write sensitivity rows."""
    fieldnames = [
        "scenario",
        "depart_km",
        "return_km",
        "max_fraction",
        "min_points",
        "season",
        "transit_routes",
        "individuals",
        "transit_points",
    ]
    with Path(path).open("w", encoding="utf-8", newline="") as target:
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
        default="data/processed/segmentation_sensitivity_summary.csv",
    )
    parser.add_argument("--min-points", type=int, default=20)
    args = parser.parse_args()

    _, groups = read_segments(args.input)
    scenarios = [
        ("baseline", 100.0, 100.0, 0.90),
        ("lower_distance_threshold", 75.0, 75.0, 0.90),
        ("higher_distance_threshold", 150.0, 150.0, 0.90),
        ("earlier_max_fraction", 100.0, 100.0, 0.85),
        ("later_max_fraction", 100.0, 100.0, 0.95),
    ]

    rows = []
    for scenario, depart_km, return_km, max_fraction in scenarios:
        trimmed, _ = trim_segments(
            groups,
            min_points=args.min_points,
            depart_km=depart_km,
            return_km=return_km,
            max_fraction=max_fraction,
        )
        for summary in summarize(trimmed):
            rows.append(
                {
                    "scenario": scenario,
                    "depart_km": depart_km,
                    "return_km": return_km,
                    "max_fraction": max_fraction,
                    "min_points": args.min_points,
                    **summary,
                }
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_rows(output_path, rows)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
