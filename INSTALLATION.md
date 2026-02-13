# 📦 Installation & Setup Guide

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ and npm installed
- Webcam or video source (optional for testing)
- Your trained models in `backend/models/`

## 🚀 One-Click Setup & Launch

### Absolute Easiest Way
```cmd
start-here.bat
```
This will:
1. Check your system
2. Identify any issues
3. Offer to launch the dashboard automatically

### Quick Launch (After Setup)
```cmd
launch.bat
```
Interactive menu with all options.

---

## 📋 Step-by-Step Setup

### 1. Create Virtual Environment
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install Backend Dependencies
```powershell
cd backend
pip install -r requirements.txt
pip install -r requirements-yolo.txt
cd ..
```

### 3. Install Frontend Dependencies
```powershell
npm install
```

### 4. Verify Models
```powershell
ls backend\models\*.pt
```
You should see:
- `yolov8_tier1.pt` (Primary routing detector)
- `yolov8_tier2.pt` (Material classifier)

### 5. Run System Check
```powershell
python check_system.py
```

### 6. Run Tests (Optional)
```powershell
.\test-dashboard.ps1
```

### 7. Launch Dashboard
```powershell
.\start-dashboard.ps1
```

---

## 🔧 Detailed Installation

### Backend Setup

```powershell
# Create and activate virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# Navigate to backend
cd backend

# Install base dependencies
pip install -r requirements.txt

# Install YOLO dependencies
pip install -r requirements-yolo.txt

# Verify installation
python -c "import ultralytics; import fastapi; print('OK')"

# Return to root
cd ..
```

### Frontend Setup

```powershell
# Install dependencies
npm install

# Verify installation
npm run build --dry-run

# Optional: Update dependencies
npm update
```

### Model Setup

Your models should already be in `backend/models/`:
```
backend/models/
  ├── yolov8_tier1.pt    (Primary routing detector)
  └── yolov8_tier2.pt    (Material classifier)
```

If models are elsewhere, update `backend/.env`:
```bash
TIER1_MODEL_PATH=path/to/your/tier1.pt
TIER2_MODEL_PATH=path/to/your/tier2.pt
```

---

## 🧪 Testing Installation

### Quick Test
```powershell
python check_system.py
```

### Comprehensive Test
```powershell
.\test-dashboard.ps1
```

### Manual Tests

#### Test Models
```powershell
cd backend\training
python test_system.py --source 0  # Webcam
python test_system.py --source test_image.jpg  # Image
```

#### Test Backend API
```powershell
# Terminal 1: Start backend
cd backend
..\venv\Scripts\Activate.ps1
uvicorn app.main:app

# Terminal 2: Test API
Invoke-WebRequest http://localhost:8000/
Invoke-WebRequest http://localhost:8000/metrics
```

#### Test Frontend
```powershell
npm run dev
# Open browser to http://localhost:5173
```

---

## 🐛 Common Issues & Solutions

### "Python not found"
```powershell
# Download from python.org
# Or use Windows Store:
winget install Python.Python.3.11
```

### "pip not found"
```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### "Node not found"
```powershell
# Download from nodejs.org
# Or use winget:
winget install OpenJS.NodeJS
```

### "Virtual environment activation failed"
```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
venv\Scripts\Activate.ps1
```

### "Models not found"
```powershell
# Verify models exist
ls backend\models\*.pt

# If missing, check training output directory
ls backend\training\runs\

# Copy from training results
cp backend\training\runs\detect\tier1\weights\best.pt backend\models\yolov8_tier1.pt
cp backend\training\runs\classify\tier2\weights\best.pt backend\models\yolov8_tier2.pt
```

### "OpenCV camera error"
```powershell
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"

# Try different camera index
$env:CAMERA_SOURCE="1"

# Check Windows camera permissions
start ms-settings:privacy-webcam
```

### "Port 8000 already in use"
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or use different port
$env:PORT="8001"
```

### "Ultralytics import error"
```powershell
# Reinstall ultralytics
pip uninstall ultralytics -y
pip install ultralytics --no-cache-dir

# Verify
python -c "from ultralytics import YOLO; print('OK')"
```

---

## 📦 Dependencies List

### Backend (Python)
- fastapi - Web framework
- uvicorn - ASGI server
- ultralytics - YOLO models
- opencv-python - Computer vision
- numpy - Numerical computing
- python-multipart - File uploads
- websockets - Real-time streaming

### Frontend (Node.js)
- react - UI framework
- typescript - Type safety
- vite - Build tool
- tailwindcss - Styling
- shadcn/ui - UI components
- recharts - Data visualization
- lucide-react - Icons

---

## 🔐 Permissions

### Windows Camera Access
1. Open Settings → Privacy & Security → Camera
2. Enable "Let apps access your camera"
3. Enable access for "Desktop apps"

### Python Script Execution
```powershell
# Allow scripts (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 💾 Disk Space Requirements

- Python packages: ~2 GB
- Node modules: ~500 MB
- Models: ~100 MB (both)
- Total: ~2.6 GB

---

## 🔄 Updating

### Update Backend
```powershell
cd backend
pip install -r requirements.txt --upgrade
pip install -r requirements-yolo.txt --upgrade
```

### Update Frontend
```powershell
npm update
```

### Update Models
Replace files in `backend/models/` with new trained models.

---

## 🗑️ Uninstallation

```powershell
# Remove virtual environment
rmdir /s venv

# Remove node modules
rmdir /s node_modules

# Remove Python packages (in venv only)
# Already removed with venv

# Keep models if needed
# Otherwise: rmdir /s backend\models
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Models present in backend/models/
- [ ] .env files created
- [ ] System check passes
- [ ] Tests pass
- [ ] Dashboard launches successfully

---

## 🆘 Getting Help

1. **System Check**: Run `python check_system.py` to identify issues
2. **Test Suite**: Run `.\test-dashboard.ps1` to test components
3. **Logs**: Check terminal output for error messages
4. **Documentation**: See `REALTIME_DASHBOARD.md` for details

---

**Ready?** Run:
```powershell
start-here.bat
```

This will check everything and start the dashboard if ready!
