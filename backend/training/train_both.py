"""
Train both dual-agent models sequentially with a single command.

Primary Agent (Detector): YOLO detection on 6 classes
Secondary Agent (Classifier): YOLO classification on 10 classes

Usage:
    python train_both.py --epochs 30 --device 0
    python train_both.py --epochs 50 --device cpu --batch 16
"""

import argparse
import subprocess
import sys
from pathlib import Path
import shutil


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ Failed: {description}")
        return False
    
    print(f"\n✅ Completed: {description}")
    return True


def copy_model(source_pattern, dest_name):
    """Copy trained model to models directory."""
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Find the best.pt file
    runs_dir = Path(__file__).parent.parent.parent / "runs"
    
    # Search for the file
    for best_pt in runs_dir.rglob("best.pt"):
        if source_pattern in str(best_pt):
            dest = models_dir / dest_name
            shutil.copy2(best_pt, dest)
            print(f"📦 Copied model: {dest.name}")
            return dest
    
    print(f"⚠ Could not find model matching: {source_pattern}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Train both dual-agent models")
    parser.add_argument("--epochs", type=int, default=30, help="Training epochs for both models")
    parser.add_argument("--device", default="0", help="Device: 0, 1, cpu")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--detector-model", default="yolov8n.pt", help="Base model for detector (yolov8n/s/m/l/x)")
    parser.add_argument("--classifier-model", default="yolov8n-cls.pt", help="Base model for classifier")
    parser.add_argument("--skip-detector", action="store_true", help="Skip detector training")
    parser.add_argument("--skip-classifier", action="store_true", help="Skip classifier training")
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("🧠 DUAL-AGENT TRAINING PIPELINE")
    print(f"{'='*60}")
    print(f"Detector model: {args.detector_model}")
    print(f"Classifier model: {args.classifier_model}")
    print(f"Epochs: {args.epochs}")
    print(f"Device: {args.device}")
    print(f"Batch size: {args.batch}")
    print(f"{'='*60}\n")
    
    success = True
    
    # Step 1: Train Primary Detector (Agent A)
    if not args.skip_detector:
        detector_cmd = (
            f'python train.py '
            f'--data "../garbage detection/GARBAGE CLASSIFICATION/data.yaml" '
            f'--model {args.detector_model} '
            f'--epochs {args.epochs} '
            f'--device {args.device} '
            f'--batch {args.batch} '
            f'--run-name detector_agent'
        )
        
        if not run_command(detector_cmd, "Training Primary Detector (Agent A - 6 classes)"):
            success = False
        else:
            # Copy detector model
            runs_dir = Path(__file__).parent.parent.parent / "runs" / "detect"
            latest_run = max(runs_dir.glob("detector_agent*"), key=lambda p: p.stat().st_mtime, default=None)
            if latest_run:
                best_pt = latest_run / "weights" / "best.pt"
                if best_pt.exists():
                    models_dir = Path(__file__).parent.parent / "models"
                    models_dir.mkdir(exist_ok=True)
                    dest = models_dir / "yolov8_tier1.pt"
                    shutil.copy2(best_pt, dest)
                    print(f"📦 Saved detector: {dest}")
    
    # Step 2: Train Secondary Classifier (Agent B)
    if success and not args.skip_classifier:
        classifier_cmd = (
            f'yolo classify train '
            f'data="../garbage classification/standardized_256" '
            f'model={args.classifier_model} '
            f'epochs={args.epochs} '
            f'imgsz=256 '
            f'device={args.device} '
            f'batch={args.batch} '
            f'project=../../runs/classify '
            f'name=classifier_agent'
        )
        
        if not run_command(classifier_cmd, "Training Secondary Classifier (Agent B - 10 classes)"):
            success = False
        else:
            # Copy classifier model
            runs_dir = Path(__file__).parent.parent.parent / "runs" / "classify"
            latest_run = max(runs_dir.glob("classifier_agent*"), key=lambda p: p.stat().st_mtime, default=None)
            if latest_run:
                best_pt = latest_run / "weights" / "best.pt"
                if best_pt.exists():
                    models_dir = Path(__file__).parent.parent / "models"
                    models_dir.mkdir(exist_ok=True)
                    dest = models_dir / "yolov8_tier2.pt"
                    shutil.copy2(best_pt, dest)
                    print(f"📦 Saved classifier: {dest}")
    
    # Final summary
    print(f"\n{'='*60}")
    if success:
        print("✅ TRAINING COMPLETE!")
        print(f"{'='*60}")
        print("\n📁 Trained models saved to: backend/models/")
        print("   - yolov8_tier1.pt (Detector - 6 classes)")
        print("   - yolov8_tier2.pt (Classifier - 10 classes)")
        print("\n🚀 Next steps:")
        print("   1. Update .env with:")
        print("      USE_REAL_INFERENCE=1")
        print("      TIER1_MODEL_PATH=models/yolov8_tier1.pt")
        print("      TIER2_MODEL_PATH=models/yolov8_tier2.pt")
        print("   2. Start backend: python -m app.main")
        print(f"{'='*60}\n")
    else:
        print("❌ TRAINING FAILED")
        print("Check errors above and retry.")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
