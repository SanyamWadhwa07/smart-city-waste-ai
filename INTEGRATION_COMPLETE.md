# 🎉 CogniRecycle Real-time Dashboard - READY TO USE!

## ✅ What's Been Integrated

Your trained dual-tier YOLO models are now fully integrated with the real-time dashboard!

### Trained Models
- ✅ **Tier 1 Model** (`backend/models/yolov8_tier1.pt`) - Primary routing agent
- ✅ **Tier 2 Model** (`backend/models/yolov8_tier2.pt`) - Material classification agent
- ✅ Environment configuration files created
- ✅ Real-time inference enabled

### Testing Scripts
- ✅ **Enhanced test_system.py** - Visual testing with statistics and video recording
- ✅ **test_integration.py** - Comprehensive integration tests
- ✅ **test-dashboard.ps1** - Quick test launcher
- ✅ **check_system.py** - Pre-flight system check

### Startup Scripts
- ✅ **start-dashboard.ps1** - Automated dashboard launcher
- ✅ **launch.bat** - Interactive menu launcher
- ✅ Configuration files with proper model paths

### Documentation
- ✅ **REALTIME_DASHBOARD.md** - Complete integration guide
- ✅ **QUICKSTART_REALTIME.md** - Quick reference commands

---

## 🚀 How to Start (3 Simple Steps)

### Step 1: Pre-flight Check
```powershell
python check_system.py
```
This verifies all dependencies and models are in place.

### Step 2: Run Tests (Optional but Recommended)
```powershell
.\test-dashboard.ps1
```
This tests your models, API, and integration.

### Step 3: Launch Dashboard
```powershell
.\start-dashboard.ps1
```
Or use the interactive launcher:
```powershell
.\launch.bat
```

**That's it!** 🎉

---

## 📊 What You'll See

### Real-time Dashboard Features

1. **Live Detection Stream**
   - Real-time video with bounding boxes
   - Dual-agent classification (Material + Routing)
   - Confidence scores displayed
   - Color-coded: Green = Agreement, Red = Contamination

2. **Analytics Dashboard**
   - Items processed counter
   - Contamination rate tracking
   - Routing efficiency metrics
   - Environmental impact (CO2 saved)
   - Economic value recovered

3. **Alerts System**
   - Real-time contamination alerts
   - Agent disagreement notifications
   - Low-confidence detections

4. **Review Queue**
   - Items flagged for manual review
   - Agent disagreement details
   - Accept/Reject workflow

---

## 🎯 Quick Commands

### Launch
```powershell
# Full dashboard
.\start-dashboard.ps1

# Interactive menu
.\launch.bat
```

### Test
```powershell
# All tests
.\test-dashboard.ps1

# Camera test only
.\test-dashboard.ps1 -TestType camera

# Models test only
.\test-dashboard.ps1 -TestType models
```

### Manual Testing
```powershell
# Test with webcam
cd backend\training
python test_system.py --source 0

# Test with video and save output
python test_system.py --source video.mp4 --save --output results.mp4
```

---

## 🌐 Access Points

Once running:

- **Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/detections

---

## ⚙️ Configuration

### Quick Settings (backend/.env)

```bash
# Enable real-time inference (already set)
USE_REAL_INFERENCE=1

# Your trained models (already configured)
TIER1_MODEL_PATH=models/yolov8_tier1.pt
TIER2_MODEL_PATH=models/yolov8_tier2.pt

# Adjust if needed:
MODEL_CONF_TIER1=0.35      # Lower = more detections
MODEL_CONF_TIER2=0.35      # Lower = more detections
CAMERA_SOURCE=0            # 0=webcam, or path/URL
MODEL_DEVICE=cpu           # or 'cuda' for GPU
```

### Camera Sources
```bash
CAMERA_SOURCE=0                    # Default webcam
CAMERA_SOURCE=1                    # Second webcam
CAMERA_SOURCE=path/to/video.mp4   # Video file
CAMERA_SOURCE=rtsp://ip:port/...  # IP camera
```

---

## 🧪 Testing Your Models

### Visual Test (Recommended First)
```powershell
cd backend\training
python test_system.py --source 0
```
**Press 'q' to quit**

This shows:
- ✓ Green boxes = Agents agree
- ✗ Red boxes = Contamination detected
- Real-time statistics overlay
- Both agent predictions displayed

### Full Integration Test
```powershell
python backend\training\test_integration.py
```

Tests:
1. Model loading and inference
2. Backend API endpoints
3. WebSocket streaming
4. Full system integration

---

## 📈 Performance Tips

### For Better Speed
```powershell
# Use smaller image size
$env:MODEL_IMGSZ="416"

# Use GPU (if available)
$env:MODEL_DEVICE="cuda"
```

### For Better Accuracy
```powershell
# Increase confidence threshold
$env:MODEL_CONF_TIER1="0.45"
$env:MODEL_CONF_TIER2="0.45"
```

### For More Detections
```powershell
# Lower confidence threshold
$env:MODEL_CONF_TIER1="0.25"
$env:MODEL_CONF_TIER2="0.25"
```

---

## 🐛 Troubleshooting

### "Models not found"
```powershell
# Check models exist
ls backend\models\*.pt

# Should see: yolov8_tier1.pt and yolov8_tier2.pt
```

### "Cannot connect to backend"
```powershell
# Verify backend is running
Invoke-WebRequest http://localhost:8000/

# Check for port conflicts
netstat -ano | findstr :8000
```

### "Camera not working"
```powershell
# Test camera
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Try different camera index
$env:CAMERA_SOURCE="1"

# Or use video file
$env:CAMERA_SOURCE="C:\path\to\video.mp4"
```

### "Dependencies missing"
```powershell
# Reinstall backend dependencies
cd backend
pip install -r requirements.txt -r requirements-yolo.txt

# Reinstall frontend dependencies
npm install
```

---

## 📚 Documentation

- **[REALTIME_DASHBOARD.md](REALTIME_DASHBOARD.md)** - Complete integration guide
- **[QUICKSTART_REALTIME.md](QUICKSTART_REALTIME.md)** - Quick reference
- **[2TIER_TRAINING_GUIDE.md](docs/2TIER_TRAINING_GUIDE.md)** - Model training details
- **[2TIER_IMPLEMENTATION_SUMMARY.md](docs/2TIER_IMPLEMENTATION_SUMMARY.md)** - Technical details

---

## 🎓 Understanding the System

### Dual-Agent Architecture

**Agent A (Material Agent)** - Tier 1 Model
- Detects waste objects in real-time
- Classifies into broad categories: PLASTIC, GLASS, METAL, PAPER, etc.
- Draws bounding boxes around objects

**Agent B (Routing Agent)** - Tier 2 Model
- Receives cropped objects from Agent A
- Performs detailed classification: plastic, glass, metal, paper, battery, etc.
- Cross-validates with Agent A

**Cross-Validation**
- Both agents must agree for final decision
- Disagreement = Contamination alert
- Low confidence = Manual review

### Metrics Tracked
- **Items processed**: Total objects detected
- **Contamination rate**: Agent disagreements / Total
- **Routing efficiency**: Correct classifications / Total
- **CO2 saved**: Environmental impact calculation
- **Value recovered**: Economic value estimation

---

## 💡 Pro Tips

1. **First Time**: Run `check_system.py` before starting
2. **Testing**: Always test with `test_system.py` first to see models in action
3. **Performance**: Start with default settings, adjust based on results
4. **Camera**: Test different angles and lighting for best results
5. **Thresholds**: Fine-tune confidence based on your accuracy requirements

---

## 🔗 API Integration

### WebSocket Example (JavaScript)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/detections');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Detection:', data.detection.label);
  console.log('Confidence:', data.detection.confidence);
  console.log('Route:', data.decision.route);
  console.log('Contamination:', data.decision.contamination_flag);
};
```

### REST API Example (Python)
```python
import requests

# Get current metrics
response = requests.get('http://localhost:8000/metrics')
metrics = response.json()
print(f"Items processed: {metrics['items_processed']}")

# Get environmental impact
response = requests.get('http://localhost:8000/impact')
impact = response.json()
print(f"CO2 saved: {impact['total_co2_kg']:.2f} kg")
```

---

## 🎬 What's Next?

Your system is fully integrated and ready! You can now:

1. ✅ **Use it live** with your webcam or IP camera
2. ✅ **Process videos** for batch analysis
3. ✅ **Integrate** with other systems via REST API or WebSocket
4. ✅ **Monitor** real-time metrics and performance
5. ✅ **Fine-tune** confidence thresholds based on results

---

## 🏆 System Status

```
✅ Models: Trained and loaded
✅ Backend: Configured for real-time inference
✅ Frontend: Dashboard ready
✅ Testing: Scripts available
✅ Documentation: Complete
✅ Ready to launch: YES!
```

---

**🎉 Congratulations! Your AI-powered waste sorting system is ready to go! 🎉**

Start with:
```powershell
python check_system.py  # Verify everything
.\test-dashboard.ps1    # Test the system
.\start-dashboard.ps1   # Launch dashboard
```

**Happy Sorting! ♻️**
