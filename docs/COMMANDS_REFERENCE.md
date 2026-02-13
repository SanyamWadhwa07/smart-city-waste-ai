# CogniRecycle: Complete Commands Reference

**Version:** 2.0  
**Platform:** Windows (PowerShell/CMD), Linux/macOS (Bash)  
**Date:** February 13, 2026

This document contains ALL commands needed to set up, run, test, and manage the CogniRecycle system.

---

## Table of Contents

1. [Initial Setup](#1-initial-setup)
2. [Backend Commands](#2-backend-commands)
3. [Frontend Commands](#3-frontend-commands)
4. [Testing Commands](#4-testing-commands)
5. [Model Training Commands](#5-model-training-commands)
6. [Docker Commands](#6-docker-commands)
7. [Development Workflows](#7-development-workflows)
8. [Troubleshooting Commands](#8-troubleshooting-commands)

---

## 1. Initial Setup

### 1.1 One-Click Setup (Windows)

```powershell
# Check system requirements and dependencies
.\start-here.bat
```

This script:
- Checks Python version (3.10+)
- Verifies backend dependencies
- Checks frontend dependencies (Node.js, npm)
- Validates model files
- Offers to launch dashboard if all checks pass

### 1.2 Manual Environment Setup

#### **Windows (PowerShell)**

```powershell
# Clone repository
git clone <repository-url>
cd smart-city-waste-ai

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-yolo.txt
cd ..

# Install frontend dependencies
npm install

# Copy environment file
copy backend\.env.example backend\.env
```

#### **Linux/macOS (Bash)**

```bash
# Clone repository
git clone <repository-url>
cd smart-city-waste-ai

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-yolo.txt
cd ..

# Install frontend dependencies
npm install

# Copy environment file
cp backend/.env.example backend/.env
```

### 1.3 System Check

```powershell
# Run pre-flight checks
python check_system.py
```

**What it checks:**
- Python version and availability
- Required Python packages
- Node.js and npm
- Model files existence
- Environment variables

---

## 2. Backend Commands

### 2.1 Start Backend Server

#### **Production Mode (Real AI Inference)**

```powershell
# Windows PowerShell
cd backend
..\venv\Scripts\Activate.ps1
$env:USE_REAL_INFERENCE="1"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Linux/macOS
cd backend
source ../venv/bin/activate
export USE_REAL_INFERENCE=1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Simulation Mode (Mock Data)**

```powershell
# Windows
cd backend
..\venv\Scripts\Activate.ps1
$env:USE_REAL_INFERENCE="0"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Linux/macOS
cd backend
source ../venv/bin/activate
export USE_REAL_INFERENCE=0
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 Backend Configuration

#### **View Current Configuration**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe -c "from app.config import ModelConfig; cfg = ModelConfig.from_env(); print(f'Tier1: {cfg.tier1_model_path}'); print(f'Tier2: {cfg.tier2_model_path}')"
```

```bash
# Linux/macOS
cd backend
../venv/bin/python -c "from app.config import ModelConfig; cfg = ModelConfig.from_env(); print(f'Tier1: {cfg.tier1_model_path}'); print(f'Tier2: {cfg.tier2_model_path}')"
```

#### **Check Environment Variable**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe -c "import os; print('USE_REAL_INFERENCE:', os.getenv('USE_REAL_INFERENCE', 'NOT SET'))"
```

```bash
# Linux/macOS
cd backend
../venv/bin/python -c "import os; print('USE_REAL_INFERENCE:', os.getenv('USE_REAL_INFERENCE', 'NOT SET'))"
```

### 2.3 Backend Health Check

```powershell
# Check if backend is running
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | ConvertFrom-Json | ConvertTo-Json
```

```bash
# Linux/macOS
curl http://localhost:8000/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-13T12:34:56",
  "pipeline_ready": true,
  "models_loaded": true,
  "camera_available": true
}
```

### 2.4 Backend API Documentation

```powershell
# Open API docs in browser
Start-Process "http://localhost:8000/docs"
```

```bash
# Linux/macOS
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
```

### 2.5 Backend Package Management

#### **Install New Package**

```powershell
# Windows
pip install <package-name>

# Add to requirements.txt
pip freeze | Select-String <package-name> >> backend\requirements.txt
```

```bash
# Linux/macOS
pip install <package-name>

# Add to requirements.txt
pip freeze | grep <package-name> >> backend/requirements.txt
```

#### **Update All Packages**

```powershell
pip install --upgrade -r backend\requirements.txt
```

---

## 3. Frontend Commands

### 3.1 Start Frontend Development Server

```powershell
# Windows/Linux/macOS
npm run dev
```

**Access:** http://localhost:5173

### 3.2 Build Frontend for Production

```powershell
# Production build
npm run build

# Development build (with source maps)
npm run build:dev
```

**Output:** `dist/` folder

### 3.3 Preview Production Build

```powershell
npm run preview
```

**Access:** http://localhost:4173

### 3.4 Frontend Linting

```powershell
# Check for linting errors
npm run lint

# Auto-fix linting errors
npm run lint -- --fix
```

### 3.5 Frontend Testing

```powershell
# Run tests once
npm test

# Run tests in watch mode
npm run test:watch
```

### 3.6 Frontend Package Management

```powershell
# Install new package
npm install <package-name>

# Install dev dependency
npm install --save-dev <package-name>

# Update all packages
npm update

# Check for outdated packages
npm outdated
```

---

## 4. Testing Commands

### 4.1 System Integration Tests

#### **Full System Test (All Components)**

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe test_integration.py
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python test_integration.py
```

**Tests:**
- Detector agent (Tier1)
- Classifier agent (Tier2)
- Decision engine
- Routing logic
- Cross-validation
- Impact tracking

### 4.2 Real-time Webcam Test

#### **Test with Webcam (Live)**

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe test_system.py --source 0
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python test_system.py --source 0
```

**Arguments:**
- `--source 0` - Default webcam
- `--source 1` - Secondary webcam
- `--source video.mp4` - Video file

#### **Test with Video File**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe test_realtime_webcam.py --source "path\to\video.mp4"
```

```bash
# Linux/macOS
cd backend
../venv/bin/python test_realtime_webcam.py --source "path/to/video.mp4"
```

#### **Test with Video + Save Output**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe test_realtime_webcam.py --source "final.mp4" --save-video
```

```bash
# Linux/macOS
cd backend
../venv/bin/python test_realtime_webcam.py --source "final.mp4" --save-video
```

**Output:** `backend/output/output_TIMESTAMP.mp4`

### 4.3 Model Validation Tests

#### **Test Detector Only (Tier1)**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe -c "from app.detector import WasteDetector; d = WasteDetector(); print(d.get_info())"
```

```bash
# Linux/macOS
cd backend
../venv/bin/python -c "from app.detector import WasteDetector; d = WasteDetector(); print(d.get_info())"
```

#### **Test Classifier Only (Tier2)**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe -c "from app.classifier import MaterialClassifier; c = MaterialClassifier(); print(c.get_info())"
```

```bash
# Linux/macOS
cd backend
../venv/bin/python -c "from app.classifier import MaterialClassifier; c = MaterialClassifier(); print(c.get_info())"
```

#### **Test Full Pipeline**

```powershell
# Windows
cd backend
..\venv\Scripts\python.exe test_pipeline_debug.py
```

```bash
# Linux/macOS
cd backend
../venv/bin/python test_pipeline_debug.py
```

### 4.4 API Endpoint Tests

#### **Test Metrics Endpoint**

```powershell
# Windows
Invoke-WebRequest -Uri "http://localhost:8000/metrics" -UseBasicParsing | ConvertFrom-Json
```

```bash
# Linux/macOS
curl http://localhost:8000/metrics | jq
```

#### **Test Impact Summary**

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/impact/summary" -UseBasicParsing | ConvertFrom-Json
```

```bash
curl http://localhost:8000/impact/summary | jq
```

#### **Test Contamination Metrics**

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/contamination/metrics" -UseBasicParsing | ConvertFrom-Json
```

```bash
curl http://localhost:8000/contamination/metrics | jq
```

#### **Test Adaptive Thresholds**

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/learning/thresholds" -UseBasicParsing | ConvertFrom-Json
```

```bash
curl http://localhost:8000/learning/thresholds | jq
```

#### **Test Review Queue**

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/review/queue" -UseBasicParsing | ConvertFrom-Json
```

```bash
curl http://localhost:8000/review/queue | jq
```

### 4.5 WebSocket Test

```powershell
# Windows (requires wscat: npm install -g wscat)
wscat -c ws://localhost:8000/ws/stream
```

```bash
# Linux/macOS
wscat -c ws://localhost:8000/ws/stream
```

### 4.6 Dataset Validation

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe validate_labels.py
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python validate_labels.py
```

---

## 5. Model Training Commands

### 5.1 Prepare Training Datasets

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe prepare_2tier_dataset.py
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python prepare_2tier_dataset.py
```

**Output:**
- `data_tier1/` - Tier1 training data
- `data_tier2/` - Tier2 training data

### 5.2 Train Tier 1 Model (Detector)

#### **CPU Training**

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe train.py --tier 1 --model yolov8m.pt --epochs 50 --batch 16 --device cpu
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python train.py --tier 1 --model yolov8m.pt --epochs 50 --batch 16 --device cpu
```

#### **GPU Training**

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe train.py --tier 1 --model yolov8m.pt --epochs 50 --batch 32 --device cuda
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python train.py --tier 1 --model yolov8m.pt --epochs 50 --batch 32 --device cuda
```

**Arguments:**
- `--tier 1` - Train Tier1 detector
- `--model yolov8m.pt` - Base model (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
- `--epochs 50` - Training epochs
- `--batch 16` - Batch size
- `--device cpu` - Device (cpu, cuda, mps)
- `--imgsz 640` - Image size (optional)

**Output:** `runs/detect/tier1/weights/best.pt`

### 5.3 Train Tier 2 Model (Classifier)

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe train.py --tier 2 --model yolov8m.pt --epochs 50 --batch 32 --device cuda
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python train.py --tier 2 --model yolov8m.pt --epochs 50 --batch 32 --device cuda
```

**Output:** `runs/classify/tier2/weights/best.pt`

### 5.4 Train Both Models Sequentially

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe train_both.py --epochs 50 --batch 32 --device cuda
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python train_both.py --epochs 50 --batch 32 --device cuda
```

### 5.5 Monitor Training (TensorBoard)

```powershell
# Windows
tensorboard --logdir backend\training\runs
```

```bash
# Linux/macOS
tensorboard --logdir backend/training/runs
```

**Access:** http://localhost:6006

### 5.6 Validate Trained Model

```powershell
# Windows
cd backend\training
..\..\venv\Scripts\python.exe -c "from ultralytics import YOLO; model = YOLO('runs/detect/tier1/weights/best.pt'); model.val()"
```

```bash
# Linux/macOS
cd backend/training
../../venv/bin/python -c "from ultralytics import YOLO; model = YOLO('runs/detect/tier1/weights/best.pt'); model.val()"
```

### 5.7 Download Pre-trained Models

```powershell
# Windows
cd backend\scripts
..\..\venv\Scripts\python.exe download_model.py
```

```bash
# Linux/macOS
cd backend/scripts
../../venv/bin/python download_model.py
```

---

## 6. Docker Commands

### 6.1 Build Docker Images

```powershell
# Build backend image
docker build -t cognirecycle-backend -f backend/Dockerfile .

# Build with GPU support
docker build -t cognirecycle-backend-gpu -f backend/Dockerfile --build-arg ENABLE_GPU=1 .
```

### 6.2 Run with Docker Compose

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### 6.3 Docker Container Management

```powershell
# List running containers
docker ps

# Stop container
docker stop <container-id>

# Remove container
docker rm <container-id>

# View container logs
docker logs <container-id>

# Execute command in container
docker exec -it <container-id> bash
```

### 6.4 Docker Cleanup

```powershell
# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove all unused data
docker system prune -a
```

---

## 7. Development Workflows

### 7.1 Full Stack Development

#### **Terminal 1: Backend**

```powershell
# Windows
cd backend
..\venv\Scripts\Activate.ps1
$env:USE_REAL_INFERENCE="1"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### **Terminal 2: Frontend**

```powershell
npm run dev
```

#### **Terminal 3: Testing**

```powershell
# Run integration tests
cd backend\training
..\..\venv\Scripts\python.exe test_integration.py
```

### 7.2 Model Development Workflow

```powershell
# 1. Prepare data
cd backend\training
..\..\venv\Scripts\python.exe prepare_2tier_dataset.py

# 2. Validate labels
..\..\venv\Scripts\python.exe validate_labels.py

# 3. Train Tier1
..\..\venv\Scripts\python.exe train.py --tier 1 --epochs 50 --device cuda

# 4. Train Tier2
..\..\venv\Scripts\python.exe train.py --tier 2 --epochs 50 --device cuda

# 5. Test models
..\..\venv\Scripts\python.exe test_integration.py

# 6. Deploy models (copy to models/)
copy runs\detect\tier1\weights\best.pt ..\models\yolov8_tier1.pt
copy runs\classify\tier2\weights\best.pt ..\models\yolov8_tier2.pt
```

### 7.3 Quick Dashboard Launch

```powershell
# Windows - One command to start everything
.\start-dashboard.ps1
```

**What it does:**
1. Activates virtual environment
2. Sets USE_REAL_INFERENCE=1
3. Starts backend in background
4. Starts frontend in background
5. Opens browser

### 7.4 Git Workflow

```powershell
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: your feature description"

# Push to remote
git push origin feature/your-feature-name

# Create pull request (GitHub/GitLab)
```

---

## 8. Troubleshooting Commands

### 8.1 Python Environment Issues

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# List installed packages
pip list

# Check for package conflicts
pip check

# Reinstall all dependencies
pip install --force-reinstall -r backend\requirements.txt
```

### 8.2 Model Loading Issues

```powershell
# Check model files exist
dir backend\models\*.pt

# Test model loading
cd backend
..\venv\Scripts\python.exe -c "from ultralytics import YOLO; model = YOLO('models/yolov8m-seg.pt'); print('Model loaded successfully')"

# Check CUDA availability
..\venv\Scripts\python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### 8.3 WebSocket Connection Issues

```powershell
# Check if backend is running
netstat -ano | findstr :8000

# Test WebSocket with curl
curl --include --no-buffer --header "Connection: Upgrade" --header "Upgrade: websocket" --header "Sec-WebSocket-Version: 13" --header "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" http://localhost:8000/ws/stream
```

### 8.4 Port Conflicts

```powershell
# Windows - Check what's using port 8000
netstat -ano | findstr :8000

# Kill process by PID
taskkill /PID <pid> /F
```

```bash
# Linux/macOS - Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <pid>
```

### 8.5 Camera Access Issues

```powershell
# Windows - List available cameras
cd backend
..\venv\Scripts\python.exe -c "import cv2; [print(f'Camera {i}:', cv2.VideoCapture(i).isOpened()) for i in range(5)]"
```

```bash
# Linux - List video devices
ls -l /dev/video*

# Check camera permissions
v4l2-ctl --list-devices
```

### 8.6 Memory/Performance Issues

```powershell
# Check system resources
Get-Process | Sort-Object -Descending PM | Select-Object -First 10

# Monitor Python process
Get-Process python | Format-Table -AutoSize

# Windows Task Manager
taskmgr
```

```bash
# Linux/macOS
htop  # or top
```

### 8.7 Clear Cache and Temporary Files

```powershell
# Python cache
Get-ChildItem -Path . -Include __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force

# Node modules cache
npm cache clean --force

# Remove build artifacts
Remove-Item -Recurse -Force dist, build, *.egg-info
```

### 8.8 Database/State Reset

```powershell
# Reset adaptive thresholds (restart backend to reload defaults)
# Stop backend, delete state files if any, restart

# Clear frontend cache
npm run build
```

### 8.9 Logs and Debugging

```powershell
# View backend logs (if using systemd/docker)
docker logs <backend-container-id>

# Check Python error logs
cat backend/logs/error.log  # if logging to file

# Enable verbose logging
$env:LOG_LEVEL="DEBUG"
```

---

## Quick Reference Cheat Sheet

### Start Development

```powershell
# Option 1: One-click
.\start-here.bat

# Option 2: Manual
# Terminal 1
cd backend
..\venv\Scripts\Activate.ps1
$env:USE_REAL_INFERENCE="1"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
npm run dev
```

### Run Tests

```powershell
# Backend integration
cd backend\training
..\..\venv\Scripts\python.exe test_integration.py

# Frontend unit tests
npm test

# Webcam test
cd backend\training
..\..\venv\Scripts\python.exe test_system.py --source 0
```

### Train Models

```powershell
cd backend\training

# Tier1
..\..\venv\Scripts\python.exe train.py --tier 1 --epochs 50 --batch 32 --device cuda

# Tier2
..\..\venv\Scripts\python.exe train.py --tier 2 --epochs 50 --batch 32 --device cuda
```

### Health Checks

```powershell
# Backend
Invoke-WebRequest http://localhost:8000/health

# Frontend
Start-Process http://localhost:5173
```

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_REAL_INFERENCE` | `0` | Enable real AI inference (0=simulate, 1=real) |
| `TIER1_MODEL_PATH` | `models/yolov8m-seg.pt` | Tier1 detector model path |
| `TIER2_MODEL_PATH` | `prithivMLmods/...` | Tier2 classifier model path/ID |
| `MODEL_DEVICE` | `auto` | Inference device (cpu, cuda, auto) |
| `ENABLE_FP16` | `auto` | Enable FP16 inference (0, 1, auto) |
| `MODEL_IMGSZ` | `640` | Detection image size |
| `MODEL_CONF_TIER1` | `0.40` | Tier1 confidence threshold |
| `MODEL_CONF_TIER2` | `0.55` | Tier2 confidence threshold |
| `CAMERA_SOURCE` | `0` | Camera index or video path |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

---

**Document Version:** 2.0  
**Last Updated:** February 13, 2026  
**Platform:** Windows (primary), Linux/macOS (secondary)
