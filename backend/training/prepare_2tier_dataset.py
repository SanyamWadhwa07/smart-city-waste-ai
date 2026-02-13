"""
Prepare 2-Tier datasets directly from Kaggle downloads in YOLO format.

Tier 1: Generic Routing (3 classes from waste-classification-data)
Tier 2: Specific Material ID (13 classes from garbage-classification)

Processes raw kaggle_downloads → YOLO format (train/val/test splits)
"""

import shutil
from pathlib import Path


# Tier 1: Dataset 1 folders → Generic classes
TIER1_CLASS_MAPPING = {
    "o": 0,           # ORGANIC
    "organic": 0,     
    "r": 1,           # RECYCLABLE
    "recyclable": 1,
}

TIER1_CLASS_NAMES = ["ORGANIC", "RECYCLABLE", "NON_RECYCLABLE"]


# Tier 2: Dataset 2 folders → Specific material classes
TIER2_CLASS_MAPPING = {
    "cardboard": 0,
    "glass": 1,
    "metal": 2,
    "paper": 3,
    "plastic": 4,
    "battery": 5,
    "biological": 6,
    "clothes": 7,
    "shoes": 8,
    "trash": 9,
    "e-waste": 10,
    "medical": 11,
    "green-glass": 12,
    # Alternate names
    "brown-glass": 1,
    "white-glass": 1,
}

TIER2_CLASS_NAMES = [
    "cardboard", "glass", "metal", "paper", "plastic", "battery",
    "biological", "clothes", "shoes", "trash", "e-waste", "medical", "green-glass"
]


def find_images_in_folder(folder: Path) -> list[Path]:
    """Find all images in a folder."""
    extensions = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG"]
    images = []
    for ext in extensions:
        images.extend(folder.glob(f"*{ext}"))
    return sorted(images)


def process_class_folder(
    class_folder: Path,
    class_id: int,
    dest_base: Path,
    split_ratio: tuple[float, float, float] = (0.7, 0.2, 0.1)
) -> dict:
    """
    Process all images from a class folder and split into train/val/test.
    Creates YOLO format labels (class_id x_center y_center width height).
    """
    images = find_images_in_folder(class_folder)
    
    if not images:
        return {"train": 0, "val": 0, "test": 0}
    
    # Calculate split indices
    total = len(images)
    train_end = int(total * split_ratio[0])
    val_end = train_end + int(total * split_ratio[1])
    
    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:],
    }
    
    counts = {}
    for split_name, split_images in splits.items():
        count = 0
        for img_path in split_images:
            try:
                # Destination paths
                dest_img_dir = dest_base / split_name / "images"
                dest_label_dir = dest_base / split_name / "labels"
                dest_img_dir.mkdir(parents=True, exist_ok=True)
                dest_label_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy image with unique name
                unique_name = f"{class_folder.name}_{img_path.stem}{img_path.suffix}"
                dest_img = dest_img_dir / unique_name
                shutil.copy2(img_path, dest_img)
                
                # Create YOLO label (whole image as object)
                # Format: class_id x_center y_center width height (all normalized 0-1)
                label_content = f"{class_id} 0.5 0.5 0.9 0.9\n"
                dest_label = dest_label_dir / f"{class_folder.name}_{img_path.stem}.txt"
                dest_label.write_text(label_content)
                
                count += 1
            except Exception as e:
                print(f"      Error: {img_path.name} - {e}")
        
        counts[split_name] = count
    
    return counts


def prepare_tier1():
    """
    Prepare Tier 1 dataset from waste-classification-data.
    Classes: ORGANIC, RECYCLABLE, NON_RECYCLABLE
    """
    source = Path("kaggle_downloads/waste-classification-data")
    dest = Path("data_tier1")
    
    print("=" * 70)
    print("TIER 1: Generic Routing Dataset")
    print("=" * 70)
    print(f"Source: {source}")
    print(f"Destination: {dest}")
    print(f"Classes: {', '.join(TIER1_CLASS_NAMES)}\n")
    
    if not source.exists():
        print(f"❌ Source not found: {source}")
        print("   Run: python download_datasets.py first\n")
        return
    
    # Clean existing
    if dest.exists():
        shutil.rmtree(dest)
    
    total_counts = {"train": 0, "val": 0, "test": 0}
    
    # Process each class folder
    for class_folder in source.rglob("*"):
        if not class_folder.is_dir():
            continue
        
        folder_name = class_folder.name.lower()
        
        if folder_name in TIER1_CLASS_MAPPING:
            class_id = TIER1_CLASS_MAPPING[folder_name]
            class_name = TIER1_CLASS_NAMES[class_id]
            
            print(f"Processing: {class_folder.name}/ → {class_name} (class {class_id})")
            
            counts = process_class_folder(class_folder, class_id, dest)
            
            for split in ["train", "val", "test"]:
                total_counts[split] += counts[split]
            
            print(f"  Train: {counts['train']}, Val: {counts['val']}, Test: {counts['test']}\n")
    
    print(f"✓ Tier 1 Complete")
    print(f"  Total → Train: {total_counts['train']}, Val: {total_counts['val']}, Test: {total_counts['test']}\n")


def prepare_tier2():
    """
    Prepare Tier 2 dataset from garbage-classification.
    Classes: 13 specific materials
    """
    source = Path("kaggle_downloads/garbage-classification")
    dest = Path("data_tier2")
    
    print("=" * 70)
    print("TIER 2: Specific Material ID Dataset")
    print("=" * 70)
    print(f"Source: {source}")
    print(f"Destination: {dest}")
    print(f"Classes ({len(TIER2_CLASS_NAMES)}): {', '.join(TIER2_CLASS_NAMES)}\n")
    
    if not source.exists():
        print(f"❌ Source not found: {source}")
        print("   Run: python download_datasets.py first\n")
        return
    
    # Clean existing
    if dest.exists():
        shutil.rmtree(dest)
    
    total_counts = {"train": 0, "val": 0, "test": 0}
    
    # Process each class folder
    for class_folder in source.rglob("*"):
        if not class_folder.is_dir():
            continue
        
        folder_name = class_folder.name.lower()
        
        if folder_name in TIER2_CLASS_MAPPING:
            class_id = TIER2_CLASS_MAPPING[folder_name]
            class_name = TIER2_CLASS_NAMES[class_id]
            
            print(f"Processing: {class_folder.name}/ → {class_name} (class {class_id})")
            
            counts = process_class_folder(class_folder, class_id, dest)
            
            for split in ["train", "val", "test"]:
                total_counts[split] += counts[split]
            
            print(f"  Train: {counts['train']}, Val: {counts['val']}, Test: {counts['test']}\n")
    
    print(f"✓ Tier 2 Complete")
    print(f"  Total → Train: {total_counts['train']}, Val: {total_counts['val']}, Test: {total_counts['test']}\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("2-TIER DATASET PREPARATION")
    print("=" * 70)
    print("Processing raw kaggle_downloads → YOLO format\n")
    
    prepare_tier1()
    prepare_tier2()
    
    print("=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    
    # Show final statistics
    tier1_train = len(list(Path("data_tier1/train/images").glob("*"))) if Path("data_tier1/train/images").exists() else 0
    tier2_train = len(list(Path("data_tier2/train/images").glob("*"))) if Path("data_tier2/train/images").exists() else 0
    
    print(f"\nDataset Statistics:")
    print(f"  Tier 1 (Generic):  {tier1_train} training images")
    print(f"  Tier 2 (Specific): {tier2_train} training images")
    
    print(f"\nDataset Locations:")
    print(f"  Tier 1: {Path('data_tier1').absolute()}")
    print(f"  Tier 2: {Path('data_tier2').absolute()}")
    
    print(f"\nNext Steps:")
    print("  1. Train Tier 1: python train.py --tier 1 --epochs 50 --model yolov8m.pt")
    print("  2. Train Tier 2: python train.py --tier 2 --epochs 50 --model yolov8m.pt")
    print("  3. Or both:      python train.py --tier both --epochs 50 --model yolov8m.pt")
