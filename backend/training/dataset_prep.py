"""
Minimal helper to stage Kaggle waste datasets into YOLO format.

The script expects the source to already have `images/` and `labels/` subfolders
with YOLO txt labels. If your dataset ships in a different structure, add your
own converter in `normalize_dataset()` or swap in a custom script.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SPLITS = ("train", "val", "test")


def normalize_dataset(src: Path, dst: Path) -> None:
    """
    Copy YOLO-style folders into the training/data directory.
    """
    for split in SPLITS:
        src_split = src / split
        if not src_split.exists():
            raise FileNotFoundError(f"Missing split: {src_split}")
        for sub in ("images", "labels"):
            source_dir = src_split / sub
            target_dir = dst / split / sub
            target_dir.mkdir(parents=True, exist_ok=True)
            if not source_dir.exists():
                raise FileNotFoundError(f"Missing {sub} in {src_split}")
            for file in source_dir.iterdir():
                if file.is_file():
                    shutil.copy(file, target_dir / file.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare YOLO dataset structure")
    parser.add_argument("--kaggle-root", required=True, type=Path, help="Path to extracted Kaggle dataset root")
    parser.add_argument(
        "--out",
        default=Path(__file__).resolve().parent / "data",
        type=Path,
        help="Output directory (will create train/val/test)",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    normalize_dataset(args.kaggle_root, args.out)
    print(f"Dataset staged at {args.out}")


if __name__ == "__main__":
    main()
