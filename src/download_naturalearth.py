"""Download Natural Earth coastline data for map figures."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from urllib.request import urlretrieve


DEFAULT_URL = (
    "https://naturalearth.s3.amazonaws.com/"
    "110m_physical/ne_110m_coastline.zip"
)


def download_file(url, output_path):
    """Download a file to output_path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(url, output_path)
    return output_path


def extract_zip(zip_path, output_dir):
    """Extract a ZIP archive."""
    zip_path = Path(zip_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(output_dir)
    return output_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--zip",
        default="data/external/naturalearth/ne_110m_coastline.zip",
    )
    parser.add_argument(
        "--extract-dir",
        default="data/external/naturalearth/ne_110m_coastline",
    )
    args = parser.parse_args()

    zip_path = download_file(args.url, args.zip)
    extract_zip(zip_path, args.extract_dir)
    print(f"Downloaded: {zip_path}")
    print(f"Extracted to: {args.extract_dir}")


if __name__ == "__main__":
    main()
