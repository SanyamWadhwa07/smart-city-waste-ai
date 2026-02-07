Training scaffold for YOLOv8 waste detection.

Quick start:
- Place datasets under `backend/training/data/` or set `--data-root`.
- Prepare YOLO structure using `python training/dataset_prep.py --kaggle-root <path>`.
- Train: `python training/train.py --data training/data.yaml --epochs 50 --model yolov8n.pt`.
- Export: `python training/train.py --export-only --weights runs/detect/train/weights/best.pt`.
