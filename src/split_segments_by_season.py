"""Split candidate migration segment points into season-specific CSV files."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def split_by_season(input_path, output_dir, prefix):
    """Split a candidate segment table by the `season` column."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {}
    writers = {}
    counts = Counter()

    try:
        with Path(input_path).open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            if "season" not in (reader.fieldnames or []):
                raise ValueError("input table must contain a 'season' column")

            for row in reader:
                season = row["season"].strip()
                if not season:
                    continue

                if season not in writers:
                    output_path = output_dir / f"{prefix}_{season}_candidate_segments.csv"
                    files[season] = output_path.open("w", encoding="utf-8", newline="")
                    writers[season] = csv.DictWriter(
                        files[season],
                        fieldnames=reader.fieldnames,
                    )
                    writers[season].writeheader()

                writers[season].writerow(row)
                counts[season] += 1
    finally:
        for file_handle in files.values():
            file_handle.close()

    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/lbbg_zeebrugge_candidate_segments.csv",
    )
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--prefix", default="lbbg_zeebrugge")
    args = parser.parse_args()

    counts = split_by_season(args.input, args.output_dir, args.prefix)
    for season, count in sorted(counts.items()):
        print(f"{season}: {count}")


if __name__ == "__main__":
    main()
