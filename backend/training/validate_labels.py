"""
Validate and fix YOLO label files.

Fixes common issues:
- Bounding box coordinates outside [0, 1] range
- Invalid format
- Empty or corrupted files
"""

from pathlib import Path
import shutil

def validate_and_fix_label(label_path):
    """Validate and fix a single label file."""
    try:
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        fixed_lines = []
        needs_fix = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                print(f"  ⚠ Invalid format in {label_path.name}: {line}")
                needs_fix = True
                continue
            
            try:
                cls_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Check if values are in valid range
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and 
                       0 <= width <= 1 and 0 <= height <= 1):
                    print(f"  ⚠ Out of range values in {label_path.name}: {line}")
                    # Clip values to valid range
                    x_center = max(0, min(1, x_center))
                    y_center = max(0, min(1, y_center))
                    width = max(0, min(1, width))
                    height = max(0, min(1, height))
                    needs_fix = True
                
                fixed_lines.append(f"{cls_id} {x_center} {y_center} {width} {height}\n")
                
            except ValueError:
                print(f"  ⚠ Invalid values in {label_path.name}: {line}")
                needs_fix = True
                continue
        
        # Write fixed file if needed
        if needs_fix and fixed_lines:
            with open(label_path, 'w') as f:
                f.writelines(fixed_lines)
            return True, False
        elif needs_fix and not fixed_lines:
            # No valid lines, delete the file
            print(f"  ✗ Deleting empty/invalid file: {label_path.name}")
            label_path.unlink()
            return True, True
        
        return False, False
        
    except Exception as e:
        print(f"  ✗ Error processing {label_path.name}: {e}")
        return False, False


def main():
    base_path = Path(__file__).parent.parent / "garbage detection" / "GARBAGE CLASSIFICATION"
    
    for split in ["train", "valid", "test"]:
        labels_dir = base_path / split / "labels"
        if not labels_dir.exists():
            print(f"⚠ Directory not found: {labels_dir}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Validating {split} labels...")
        print(f"{'='*60}")
        
        label_files = list(labels_dir.glob("*.txt"))
        print(f"Found {len(label_files)} label files")
        
        fixed_count = 0
        deleted_count = 0
        
        for label_file in label_files:
            was_fixed, was_deleted = validate_and_fix_label(label_file)
            if was_fixed:
                fixed_count += 1
            if was_deleted:
                deleted_count += 1
        
        print(f"\n✓ {split}: Fixed {fixed_count} files, Deleted {deleted_count} invalid files")
    
    print(f"\n{'='*60}")
    print("✅ Validation complete! You can now retry training.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
