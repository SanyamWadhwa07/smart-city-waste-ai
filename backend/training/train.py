"""
Lightweight YOLOv8 training scaffold.

Examples:
  python training/train.py --data training/data.yaml --model yolov8n.pt --epochs 50
  python training/train.py --export-only --weights runs/detect/train/weights/best.pt
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def train(args: argparse.Namespace) -> Path:
    model = YOLO(args.model)
    result = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        name=args.run_name,
    )
    best = Path(result.save_dir) / "weights" / "best.pt"
    print(f"Training complete. Best weights: {best}")
    return best


def export(weights: Path, fmt: str, device: str) -> None:
    model = YOLO(weights)
    out = model.export(format=fmt, device=device)
    print(f"Exported: {out}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLOv8 waste model")
    parser.add_argument("--data", default="training/data.yaml", help="data yaml path")
    parser.add_argument("--model", default="yolov8n.pt", help="base model")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--run-name", default="cognirecycle")
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--weights", type=Path, help="path to weights to export")
    parser.add_argument("--export-format", default="onnx", choices=["onnx", "engine", "torchscript"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.export_only:
        if not args.weights:
            raise SystemExit("Provide --weights when using --export-only")
        export(args.weights, args.export_format, args.device)
        return

    best = train(args)
    export(best, args.export_format, args.device)


if __name__ == "__main__":
    main()
