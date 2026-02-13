# Backend (FastAPI)

This folder contains a minimal FastAPI service that simulates YOLO detections and routes waste items to streams.

## Run locally

```powershell
cd e:\kaggle\smart-city-waste-ai\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-yolo.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `GET /metrics`
- `WS /ws/detections`

The WebSocket streams simulated detection events every 1-2 seconds.

## Real YOLO inference (optional)

Set these env vars to enable camera inference:

- `USE_REAL_INFERENCE=1`
- `MODEL_PATH=models/yolov8n.pt`
- `CAMERA_SOURCE=0`

If dependencies are missing, the service falls back to simulated detections.

## Docker

Build without YOLO (fast):

```powershell
docker compose build
docker compose up
```

Build with YOLO dependencies:

```powershell
docker compose build --build-arg INSTALL_YOLO=1 backend
docker compose up
```

## Model bootstrap

```powershell
python scripts/download_model.py --name yolov8n.pt
```

## Training scaffold

- Prep data: `python training/dataset_prep.py --kaggle-root <path-to-yolo-ready-dataset>`
- Train: `python training/train.py --data training/data.yaml --epochs 50 --model yolov8n.pt`
- Export only: `python training/train.py --export-only --weights <path> --export-format onnx`
