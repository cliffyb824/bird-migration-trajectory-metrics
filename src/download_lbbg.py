"""Download and extract the LBBG_ZEEBRUGGE Darwin Core Archive."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from urllib.request import urlretrieve


DEFAULT_URL = "https://ipt.inbo.be/archive.do?r=lbbg_zeebrugge&v=1.3"


def download_archive(url, output_path):
    """Download a Darwin Core Archive file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, output_path)
    return output_path


def extract_archive(archive_path, output_dir):
    """Extract a Darwin Core Archive ZIP file."""
    archive_path = Path(archive_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "r") as zf:
        zf.extractall(output_dir)
    return output_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--archive",
        default="data/raw/lbbg_zeebrugge_v1_3_dwca.zip",
        help="output archive path",
    )
    parser.add_argument(
        "--extract-dir",
        default="data/raw/lbbg_zeebrugge",
        help="directory for extracted files",
    )
    args = parser.parse_args()

    archive = download_archive(args.url, args.archive)
    extract_archive(archive, args.extract_dir)
    print(f"Downloaded: {archive}")
    print(f"Extracted to: {args.extract_dir}")


if __name__ == "__main__":
    main()
