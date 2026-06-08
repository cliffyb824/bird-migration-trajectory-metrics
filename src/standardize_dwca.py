"""Standardize a Darwin Core occurrence table for trajectory analysis.

The output schema is intentionally small:
- individual_id
- timestamp
- latitude
- longitude
- species

This script uses only Python's standard library so it can run before project
dependencies are installed.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_COLUMNS = {
    "individual_id": "organismID",
    "timestamp": "eventDate",
    "latitude": "decimalLatitude",
    "longitude": "decimalLongitude",
    "species": "scientificName",
    "event_type": "eventType",
}


def parse_float(value):
    """Parse a float, returning None for invalid values."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def standardize_occurrence(input_path, output_path, gps_only=True, max_rows=None):
    """Standardize occurrence records to the prototype trajectory schema."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    rows_seen = 0
    with input_path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        missing = [
            column
            for column in DEFAULT_COLUMNS.values()
            if column not in (reader.fieldnames or [])
        ]
        if missing:
            raise ValueError(f"missing expected columns: {missing}")

        with output_path.open("w", encoding="utf-8", newline="") as target:
            fieldnames = [
                "individual_id",
                "timestamp",
                "latitude",
                "longitude",
                "species",
            ]
            writer = csv.DictWriter(target, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                rows_seen += 1
                if gps_only and row[DEFAULT_COLUMNS["event_type"]] != "gps":
                    continue

                individual_id = row[DEFAULT_COLUMNS["individual_id"]].strip()
                timestamp = row[DEFAULT_COLUMNS["timestamp"]].strip()
                latitude = parse_float(row[DEFAULT_COLUMNS["latitude"]])
                longitude = parse_float(row[DEFAULT_COLUMNS["longitude"]])
                species = row[DEFAULT_COLUMNS["species"]].strip()

                if not individual_id or not timestamp:
                    continue
                if latitude is None or longitude is None:
                    continue

                writer.writerow(
                    {
                        "individual_id": individual_id,
                        "timestamp": timestamp,
                        "latitude": latitude,
                        "longitude": longitude,
                        "species": species,
                    }
                )
                rows_written += 1

                if max_rows is not None and rows_written >= max_rows:
                    break

    return rows_seen, rows_written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/raw/lbbg_zeebrugge/occurrence.txt",
        help="path to the Darwin Core occurrence table",
    )
    parser.add_argument(
        "--output",
        default="data/processed/lbbg_zeebrugge_standardized.csv",
        help="standardized CSV output path",
    )
    parser.add_argument(
        "--include-non-gps",
        action="store_true",
        help="include non-GPS events such as tag attachment records",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="optional row limit for quick prototypes",
    )
    args = parser.parse_args()

    rows_seen, rows_written = standardize_occurrence(
        args.input,
        args.output,
        gps_only=not args.include_non_gps,
        max_rows=args.max_rows,
    )
    print(f"Read {rows_seen} source rows")
    print(f"Wrote {rows_written} standardized rows to {args.output}")


if __name__ == "__main__":
    main()
