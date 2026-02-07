"""
Download a YOLO model file into backend/models.

Usage:
  python scripts/download_model.py --name yolov8n.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlretrieve

DEFAULT_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"


def download(model_url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {model_url} -> {dest}")
    urlretrieve(model_url, dest)  # nosec
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YOLO weights")
    parser.add_argument("--name", default="yolov8n.pt", help="Model filename")
    parser.add_argument("--url", default=DEFAULT_URL, help="Model download URL")
    parser.add_argument(
        "--out-dir",
        default=Path(__file__).resolve().parents[1] / "models",
        type=Path,
        help="Destination directory",
    )
    args = parser.parse_args()

    dest = args.out_dir / args.name
    if dest.exists():
        print(f"Model already exists at {dest}")
        return

    download(args.url, dest)


if __name__ == "__main__":
    main()
