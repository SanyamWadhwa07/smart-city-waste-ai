"""
2-Tier YOLOv8 training system for CogniRecycle.

Tier 1: Generic Routing (3 classes - ORGANIC, RECYCLABLE, NON_RECYCLABLE) - Material Agent
Tier 2: Specific Material ID (13 classes - cardboard, glass, metal, etc.) - Routing Agent

Examples:
  # Train Tier 1 model (Generic Routing / Material Agent)
  python train.py --tier 1 --epochs 50 --model yolov8m.pt
  
  # Train Tier 2 model (Specific Material ID / Routing Agent)
  python train.py --tier 2 --epochs 50 --model yolov8m.pt
  
  # Train both tiers sequentially
  python train.py --tier both --epochs 50
  
  # Export trained model
  python train.py --export-only --weights runs/detect/tier1/weights/best.pt --tier 1
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
    print(f"✓ Training complete. Best weights: {best}")
    return best


def export(weights: Path, fmt: str, device: str, output_name: str = None) -> Path:
    model = YOLO(weights)
    out = model.export(format=fmt, device=device)
    exported_path = Path(out)
    
    # Copy to models directory with appropriate name
    if output_name:
        models_dir = Path(__file__).parent.parent / "models"
        models_dir.mkdir(exist_ok=True)
        dest = models_dir / f"{output_name}.pt"
        import shutil
        shutil.copy2(weights, dest)
        print(f"✓ Copied to: {dest}")
    
    print(f"✓ Exported: {exported_path}")
    return exported_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train 2-Tier YOLOv8 waste detection system")
    parser.add_argument(
        "--tier",
        default="both",
        choices=["1", "2", "both"],
        help="Which tier to train: 1 (Generic/Material Agent), 2 (Specific/Routing Agent), or both",
    )
    parser.add_argument("--data", help="custom data yaml path (overrides --tier)")
    parser.add_argument("--model", default="yolov8m.pt", help="base model (yolov8n/s/m/l/x)")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--run-name", help="custom run name (auto-generated if not specified)")
    parser.add_argument("--export-only", action="store_true")
    parser.add_argument("--weights", type=Path, help="path to weights to export")
    parser.add_argument("--export-format", default="onnx", choices=["onnx", "engine", "torchscript", "pt"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    if args.export_only:
        if not args.weights:
            raise SystemExit("❌ Provide --weights when using --export-only")
        tier_name = f"tier{args.tier}" if args.tier in ["1", "2"] else "model"
        export(args.weights, args.export_format, args.device, output_name=tier_name)
        return

    # Determine which tier(s) to train
    tiers_to_train = []
    if args.tier == "both":
        tiers_to_train = ["1", "2"]
    else:
        tiers_to_train = [args.tier]

    trained_models = {}
    
    # Save original data path (if user provided custom one)
    original_data_path = args.data
    
    for tier in tiers_to_train:
        print(f"\n{'='*60}")
        if tier == "1":
            print("🔷 Training Tier 1: Generic Routing (Material Agent)")
            print("   Classes: ORGANIC, RECYCLABLE, NON_RECYCLABLE")
        else:
            print("🔶 Training Tier 2: Specific Material ID (Routing Agent)")
            print("   Classes: cardboard, glass, metal, paper, plastic, battery, etc.")
        print(f"{'='*60}\n")
        
        # Set data yaml path for THIS tier
        if original_data_path:
            data_path = original_data_path
        else:
            data_path = f"data_tier{tier}.yaml"
        
        # Set run name
        run_name = args.run_name if args.run_name else f"tier{tier}"
        
        # Update args for this tier
        args.data = data_path
        args.run_name = run_name
        
        # Train
        best_weights = train(args)
        trained_models[tier] = best_weights
        
        # Export
        output_name = f"yolov8_tier{tier}"
        export(best_weights, args.export_format, args.device, output_name=output_name)
    
    # Summary
    print(f"\n{'='*60}")
    print("✅ Training Complete!")
    print(f"{'='*60}")
    for tier, weights in trained_models.items():
        tier_name = "Material Agent (Generic)" if tier == "1" else "Routing Agent (Specific)"
        print(f"  Tier {tier} ({tier_name}): {weights}")
    print(f"\n📁 Models deployed to: backend/models/")
    print(f"\n🚀 Next: Start backend with both models for dual-agent inference")


if __name__ == "__main__":
    main()
