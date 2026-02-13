"""
Server GPU Training Script — Smart Waste AI (2-Tier System)
===========================================================

Simple script for training on your own GPU server.
No interactive components - just point to your datasets and run.

Dataset Structure Expected:
---------------------------
GARBAGE_CLASSIFICATION/     # Tier 1 - Detection
├── data.yaml
├── train/ (images + labels)
└── valid/ (images + labels)

standardized_256_split/     # Tier 2 - Classification
├── train/ (battery, biological, cardboard, etc.)
└── val/ (same classes)

Usage:
------
python server_gpu_train.py
"""

import os
import sys
from pathlib import Path
import shutil
from ultralytics import YOLO
import torch
from datetime import datetime

# ============================================================================
# CONFIGURATION — EDIT THESE PATHS
# ============================================================================

# Dataset paths (relative to project root or absolute)
BASE_DIR = Path(__file__).parent.parent  # backend/
DETECTION_DATASET = BASE_DIR / "garbage detection/GARBAGE CLASSIFICATION"
CLASSIFICATION_DATASET = BASE_DIR / "garbage classification/standardized_256_split"

# Model selection
DETECTOR_MODEL = "yolov8s.pt"       # yolov8n/s/m/l/x.pt (s=good balance)
CLASSIFIER_MODEL = "yolov8s-cls.pt"  # yolov8n/s/m/l/x-cls.pt

# Training parameters
DETECTOR_EPOCHS = 50
DETECTOR_BATCH = 16
DETECTOR_IMG_SIZE = 640

CLASSIFIER_EPOCHS = 50
CLASSIFIER_BATCH = 32
CLASSIFIER_IMG_SIZE = 256

# Output directory
OUTPUT_DIR = BASE_DIR / "models"
RUNS_DIR = Path("./runs")  # Training logs

# ============================================================================
# ENVIRONMENT CHECK
# ============================================================================

def check_environment():
    """Verify GPU and dependencies."""
    print("=" * 70)
    print("🔧 ENVIRONMENT CHECK")
    print("=" * 70)
    
    print(f"Python: {sys.version.split()[0]}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠️  WARNING: No GPU detected! Training will be very slow.")
    
    print()

# ============================================================================
# DATASET VERIFICATION
# ============================================================================

def verify_datasets():
    """Check if datasets exist and are properly structured."""
    print("=" * 70)
    print("🔍 VERIFYING DATASETS")
    print("=" * 70)
    
    # Ensure paths are Path objects
    detection_path = Path(DETECTION_DATASET)
    classification_path = Path(CLASSIFICATION_DATASET)
    
    # Check detection dataset
    detection_yaml = detection_path / "data.yaml"
    if not detection_yaml.exists():
        print(f"❌ Detection data.yaml not found at: {detection_yaml}")
        print(f"   Looking in: {detection_path}")
        sys.exit(1)
    
    print(f"✅ Detection dataset: {detection_path}")
    
    # Check classification dataset
    classification_train = classification_path / "train"
    if not classification_train.exists():
        print(f"❌ Classification train folder not found at: {classification_train}")
        sys.exit(1)
    
    classes = [d.name for d in classification_train.iterdir() if d.is_dir()]
    print(f"✅ Classification dataset: {classification_path}")
    print(f"   Classes ({len(classes)}): {', '.join(classes)}")
    print()

# ============================================================================
# TRAINING TIER 1 — OBJECT DETECTION
# ============================================================================

def train_detector():
    """Train Tier 1 object detection model."""
    print("=" * 70)
    print("🚀 TRAINING TIER 1: OBJECT DETECTION")
    print("=" * 70)
    print(f"Model: {DETECTOR_MODEL}")
    print(f"Epochs: {DETECTOR_EPOCHS}")
    print(f"Batch size: {DETECTOR_BATCH}")
    print(f"Image size: {DETECTOR_IMG_SIZE}")
    print()
    
    # Initialize model
    detector = YOLO(DETECTOR_MODEL)
    
    # Train
    results = detector.train(
        data=str(Path(DETECTION_DATASET) / "data.yaml"),
        epochs=DETECTOR_EPOCHS,
        imgsz=DETECTOR_IMG_SIZE,
        batch=DETECTOR_BATCH,
        device=0 if torch.cuda.is_available() else "cpu",
        workers=4,
        patience=15,
        save=True,
        plots=True,
        verbose=True,
        cos_lr=True,
        optimizer="AdamW",
        project=str(RUNS_DIR / "detect"),
        name="tier1_detector",
        exist_ok=True,
        save_period=10  # Save checkpoint every 10 epochs
    )
    
    print("\n✅ Tier 1 Detection training completed!")
    return results

# ============================================================================
# TRAINING TIER 2 — CLASSIFICATION
# ============================================================================

def train_classifier():
    """Train Tier 2 image classification model."""
    print("\n" + "=" * 70)
    print("🚀 TRAINING TIER 2: IMAGE CLASSIFICATION")
    print("=" * 70)
    print(f"Model: {CLASSIFIER_MODEL}")
    print(f"Epochs: {CLASSIFIER_EPOCHS}")
    print(f"Batch size: {CLASSIFIER_BATCH}")
    print(f"Image size: {CLASSIFIER_IMG_SIZE}")
    print()
    
    # Initialize model
    classifier = YOLO(CLASSIFIER_MODEL)
    
    # Train
    results = classifier.train(
        data=str(Path(CLASSIFICATION_DATASET)),
        epochs=CLASSIFIER_EPOCHS,
        imgsz=CLASSIFIER_IMG_SIZE,
        batch=CLASSIFIER_BATCH,
        device=0 if torch.cuda.is_available() else "cpu",
        workers=4,
        patience=10,
        save=True,
        plots=True,
        verbose=True,
        project=str(RUNS_DIR / "classify"),
        name="tier2_classifier",
        exist_ok=True,
        save_period=10  # Save checkpoint every 10 epochs
    )
    
    print("\n✅ Tier 2 Classification training completed!")
    return results

# ============================================================================
# MODEL VALIDATION
# ============================================================================

def validate_models():
    """Validate both trained models."""
    print("\n" + "=" * 70)
    print("📊 VALIDATING MODELS")
    print("=" * 70)
    
    # Validate detector
    detector_best = RUNS_DIR / "detect/tier1_detector/weights/best.pt"
    if detector_best.exists():
        print("\n🔍 Tier 1 Detector:")
        det_model = YOLO(str(detector_best))
        det_metrics = det_model.val()
        
        print(f"   mAP50: {det_metrics.box.map50:.4f}")
        print(f"   mAP50-95: {det_metrics.box.map:.4f}")
        print(f"   Precision: {det_metrics.box.mp:.4f}")
        print(f"   Recall: {det_metrics.box.mr:.4f}")
    else:
        print("⚠️  Detector model not found")
    
    # Validate classifier
    classifier_best = RUNS_DIR / "classify/tier2_classifier/weights/best.pt"
    if classifier_best.exists():
        print("\n🔍 Tier 2 Classifier:")
        cls_model = YOLO(str(classifier_best))
        cls_metrics = cls_model.val()
        
        print(f"   Top-1 Accuracy: {cls_metrics.top1:.4f}")
        print(f"   Top-5 Accuracy: {cls_metrics.top5:.4f}")
    else:
        print("⚠️  Classifier model not found")
    print()

# ============================================================================
# SAVE FINAL MODELS
# ============================================================================

def save_models():
    """Copy trained models to backend/models/ directory."""
    print("=" * 70)
    print("💾 SAVING MODELS")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Copy detection model
    detector_best = RUNS_DIR / "detect/tier1_detector/weights/best.pt"
    detector_last = RUNS_DIR / "detect/tier1_detector/weights/last.pt"
    
    if detector_best.exists():
        shutil.copy2(detector_best, OUTPUT_DIR / "yolov8_tier1.pt")
        shutil.copy2(detector_last, OUTPUT_DIR / "yolov8_tier1_last.pt")
        print(f"✅ Saved: {OUTPUT_DIR / 'yolov8_tier1.pt'}")
        print(f"✅ Saved: {OUTPUT_DIR / 'yolov8_tier1_last.pt'}")
    
    # Copy classification model
    classifier_best = RUNS_DIR / "classify/tier2_classifier/weights/best.pt"
    classifier_last = RUNS_DIR / "classify/tier2_classifier/weights/last.pt"
    
    if classifier_best.exists():
        shutil.copy2(classifier_best, OUTPUT_DIR / "yolov8_tier2.pt")
        shutil.copy2(classifier_last, OUTPUT_DIR / "yolov8_tier2_last.pt")
        print(f"✅ Saved: {OUTPUT_DIR / 'yolov8_tier2.pt'}")
        print(f"✅ Saved: {OUTPUT_DIR / 'yolov8_tier2_last.pt'}")
    
    print(f"\n📁 All models saved to: {OUTPUT_DIR.absolute()}")
    print(f"📊 Training logs in: {RUNS_DIR.absolute()}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main training pipeline."""
    start_time = datetime.now()
    
    print("\n" + "=" * 70)
    print("🏭 SMART WASTE AI — SERVER GPU TRAINING")
    print("=" * 70)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. Environment check
        check_environment()
        
        # 2. Verify datasets
        verify_datasets()
        
        # 3. Train Tier 1 (Detection)
        train_detector()
        
        # 4. Train Tier 2 (Classification)
        train_classifier()
        
        # 5. Validate both models
        validate_models()
        
        # 6. Save models to backend/models/
        save_models()
        
        # Completion
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration}")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
