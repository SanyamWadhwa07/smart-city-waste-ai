# CogniRecycle Model Training Guide

Complete guide for training YOLOv8 waste detection model with 24+ waste categories.

---

## 📋 Prerequisites

- Python 3.9+
- Kaggle account and API credentials
- GPU recommended (NVIDIA with CUDA) or use Google Colab
- ~5GB disk space for datasets

---

## 🚀 Quick Start

```bash
# 1. One-time setup
python setup.py

# 2. Train model (4-6 hours on RTX 3060)
python train.py --data data.yaml --epochs 50

# 3. Deploy model
cp runs/detect/cognirecycle/weights/best.pt ../models/yolov8m_waste.pt
```

---

## 📦 Dataset Preparation

### Option 1: Automatic Setup (Recommended)

```bash
python setup.py
```

This script will:
1. ✅ Verify Kaggle API configuration
2. ✅ Install all required packages
3. ✅ Download **Waste Classification Data V2** (25,000+ images)
4. ✅ Download **Garbage Classification V2** (19,762 images)
5. ✅ Convert to YOLO format with proper splits
6. ✅ Generate `data.yaml` configuration

### Option 2: Manual Setup

**Step 1: Configure Kaggle API**
```bash
# Get API key from https://www.kaggle.com/settings
# Place kaggle.json in appropriate directory:

# Windows:
mkdir %USERPROFILE%\.kaggle
copy kaggle.json %USERPROFILE%\.kaggle\

# Linux/Mac:
mkdir -p ~/.kaggle
mv kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Step 2: Install dependencies**
```bash
pip install -r ../requirements.txt
pip install -r ../requirements-yolo.txt
```

**Step 3: Download datasets**
```bash
python download_datasets.py
```

**Step 4: Verify structure**
```
training/
├── data/
│   ├── train/
│   │   ├── images/  (~30,000 images)
│   │   └── labels/  (~30,000 .txt files)
│   ├── val/
│   │   ├── images/  (~8,000 images)
│   │   └── labels/
│   └── test/
│       ├── images/  (~6,000 images)
│       └── labels/
└── data.yaml
```

---

## 🎯 Training

### Basic Training

```bash
# Train YOLOv8m for 50 epochs
python train.py --data data.yaml --epochs 50
```

### Advanced Training Options

```bash
# Full configuration
python train.py \
  --data data.yaml \
  --model yolov8m.pt \
  --epochs 100 \
  --imgsz 640 \
  --batch 16 \
  --device 0 \
  --run-name cognirecycle_v2
```

**Parameters Explained:**
- `--data`: Dataset configuration file
- `--model`: Base model (n/s/m/l/x - nano to extra-large)
- `--epochs`: Number of training epochs (50+ recommended)
- `--imgsz`: Input image size (640 standard, 1280 for high-res)
- `--batch`: Batch size (adjust based on GPU memory)
- `--device`: GPU index (0, 1) or 'cpu'
- `--run-name`: Experiment name for tracking

**Model Selection Guide:**
| Model | Speed | Accuracy | GPU Memory | Use Case |
|-------|-------|----------|------------|----------|
| yolov8n | Fastest | Good | 2GB | Edge devices, Pi |
| yolov8s | Fast | Better | 4GB | Budget GPUs |
| yolov8m | Balanced | Best | 8GB | **Recommended** |
| yolov8l | Slow | Excellent | 12GB | High accuracy needs |
| yolov8x | Slowest | Best | 16GB+ | Research/benchmarking |

### Training on Google Colab

```python
# 1. Install ultralytics
!pip install ultralytics kaggle

# 2. Upload kaggle.json to Colab
from google.colab import files
uploaded = files.upload()  # Upload kaggle.json

!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# 3. Clone repository
!git clone YOUR_REPO_URL
%cd smart-city-waste-ai/backend/training

# 4. Download datasets
!python download_datasets.py

# 5. Train with T4 GPU (free tier)
!python train.py --data data.yaml --epochs 50 --batch 32 --device 0

# 6. Download trained model
files.download('runs/detect/cognirecycle/weights/best.pt')
```

---

## 📊 Training Results

Results are saved to `runs/detect/cognirecycle/`:

```
runs/detect/cognirecycle/
├── weights/
│   ├── best.pt           # Best checkpoint (highest mAP)
│   └── last.pt           # Last epoch checkpoint
├── results.png           # Training curves (loss, mAP, etc.)
├── confusion_matrix.png  # Classification confusion matrix
├── F1_curve.png         # F1 score vs confidence
├── PR_curve.png         # Precision-Recall curve
└── val_batch0_pred.jpg  # Validation predictions sample
```

### Expected Performance Metrics (50 epochs, YOLOv8m)

| Metric | Target | Typical Range |
|--------|--------|---------------|
| **mAP@0.5** | >90% | 88-92% |
| **mAP@0.5:0.95** | >75% | 72-78% |
| **Precision** | >93% | 90-94% |
| **Recall** | >90% | 86-90% |
| **F1 Score** | >91% | 88-92% |

---

## 📤 Model Export & Deployment

### Export to ONNX (Recommended for Production)

```bash
python train.py \
  --export-only \
  --weights runs/detect/cognirecycle/weights/best.pt \
  --export-format onnx
```

### Export to TensorRT (NVIDIA Jetson/Edge Devices)

```bash
python train.py \
  --export-only \
  --weights runs/detect/cognirecycle/weights/best.pt \
  --export-format engine \
  --device 0
```

### Deploy to Backend

```bash
# Copy PyTorch model
cp runs/detect/cognirecycle/weights/best.pt ../models/yolov8m_waste.pt

# Or ONNX version (faster inference)
cp runs/detect/cognirecycle/weights/best.onnx ../models/yolov8m_waste.onnx

# Update backend/.env
echo "MODEL_PATH=models/yolov8m_waste.pt" >> ../env
```

---

## 🎯 Detected Classes (24 Categories)

The model is trained to detect:

**Recyclables (11):**
- plastic_bottle, plastic_container, plastic_bag
- glass_bottle, glass_jar
- aluminum_can, steel_can  
- paper, cardboard, newspaper, magazine

**Organic Waste (5):**
- food_scrap, fruit_peel, vegetable_waste, organic

**E-Waste (2):**
- battery, electronics

**Textiles (2):**
- clothing, fabric

**Hazardous (2):**
- chemical_container, aerosol_can

**Non-Recyclable (2):**
- styrofoam, trash

**Mixed (1):**
- recyclable_mixed

---

## 🐛 Troubleshooting

### GPU Out of Memory
```bash
# Reduce batch size
python train.py --data data.yaml --batch 8

# Or use smaller model
python train.py --data data.yaml --model yolov8s.pt
```

### No Images Found
```bash
# Verify dataset
ls data/train/images | wc -l  # Should show 30,000+

# Re-download if empty
rm -rf data/
python download_datasets.py
```

### Low Accuracy (<80%)
- Train for more epochs (100+)
- Use larger model (yolov8l.pt)
- Check for mislabeled data
- Increase dataset size with augmentation

### Training Too Slow
- Use Google Colab T4 GPU (free)
- Reduce image size (--imgsz 416)
- Use smaller model (yolov8n.pt)
- Decrease batch size

---

## ⚡ Performance Benchmarks

### Training Time (50 epochs, YOLOv8m, 44K images)

| Hardware | Time | Cost |
|----------|------|------|
| NVIDIA RTX 4090 | 2-3h | $0 (local) |
| NVIDIA RTX 3060 | 4-6h | $0 (local) |
| Google Colab T4 | 6-8h | Free |
| Google Colab A100 | 1-2h | ~$12 |
| AWS g4dn.xlarge | 5-7h | ~$5 |

### Inference Speed (FPS on 640x640 images)

| Device | YOLOv8n | YOLOv8m | YOLOv8l |
|--------|---------|---------|---------|
| RTX 4090 | 120 FPS | 80 FPS | 50 FPS |
| RTX 3060 | 65 FPS | 28 FPS | 15 FPS |
| GTX 1660 | 45 FPS | 20 FPS | 10 FPS |
| Intel i7 (CPU) | 15 FPS | 5 FPS | 2 FPS |
| Raspberry Pi 4 | 3 FPS | 1 FPS | <1 FPS |

---

## 🔄 Fine-Tuning & Transfer Learning

### Resume Training from Checkpoint
```bash
python train.py \
  --data data.yaml \
  --model runs/detect/cognirecycle/weights/last.pt \
  --epochs 50
```

### Transfer from Custom Dataset
```bash
# Start from your previous best model
python train.py \
  --data new_data.yaml \
  --model runs/detect/cognirecycle/weights/best.pt \
  --epochs 30
```

---

## 📚 Next Steps

After successful training:

1. **Deploy Model**
   ```bash
   cp runs/detect/cognirecycle/weights/best.pt ../models/yolov8m_waste.pt
   ```

2. **Configure Backend**
   ```bash
   cd ../
   cp .env.example .env
   # Edit .env: MODEL_PATH=models/yolov8m_waste.pt
   ```

3. **Start System**
   ```bash
   # Terminal 1: Backend
   uvicorn app.main:app --reload

   # Terminal 2: Frontend
   cd ../../
   npm run dev
   ```

4. **Test Detection**
   - Point camera at waste items
   - Verify real-time detection
   - Check accuracy on dashboard

---

## 📖 Additional Resources

- **Full Setup Guide**: `../IMPLEMENTATION_GUIDE.md`
- **Technical Plan**: `../../docs/plan.md`
- **Quick Commands**: `../../QUICKSTART.md`
- **Ultralytics Docs**: https://docs.ultralytics.com/

---

**Last Updated:** February 8, 2026  
**Version:** 1.0  
**Status:** Production Ready
