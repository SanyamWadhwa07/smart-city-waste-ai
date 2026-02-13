# CogniRecycle - Technical Features Implementation

**Team:** BruteForce  
**Institute:** Thapar University, Patiala  
**Team Members:** Sanyam Wadhwa (AI/ML Lead), Pratham Garg (Full Stack Developer)  
**Date:** February 7, 2026

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Feature 1: Real-Time Waste Detection Engine](#feature-1-real-time-waste-detection-engine)
3. [Feature 2: Dual-Agent Intelligent Routing System](#feature-2-dual-agent-intelligent-routing-system)
4. [Feature 3: Contamination Prevention Module](#feature-3-contamination-prevention-module)
5. [Feature 4: Environmental & Economic Impact Dashboard](#feature-4-environmental--economic-impact-dashboard)
6. [Feature 5: Adaptive Learning System](#feature-5-adaptive-learning-system)
7. [Technology Stack](#technology-stack)

---

## System Architecture Overview

### High-Level Architecture

The CogniRecycle system consists of four primary layers:

```
┌─────────────────────────────────────────────────────────────┐
│                      Input Layer                             │
│  Camera Feed → Frame Capture (30 FPS) → Preprocessing       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Detection Layer                            │
│  YOLOv8 Object Detection → Confidence Scores → Classes      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                 Intelligence Layer                           │
│  Material Agent + Routing Agent → Conflict Detection        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Application Layer                           │
│  Dashboard → Analytics → Alerts → Impact Metrics            │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: Camera captures video feed at 30 FPS
2. **Detection**: YOLOv8 processes frames and identifies waste objects
3. **Classification**: Dual-agent system determines material type and recyclability
4. **Decision**: Routing decision made (Recyclable/Organic/Landfill/Hazardous)
5. **Storage**: Decision logged to PostgreSQL database
6. **Analysis**: Contamination detector monitors patterns
7. **Output**: Dashboard displays real-time results and metrics

---

## Feature 1: Real-Time Waste Detection Engine

### Overview
Multi-object detection system capable of identifying 30+ waste categories with 95%+ accuracy at 30 FPS processing speed.

### Technical Specifications

#### Model Architecture
- **Base Model**: YOLOv8m (medium variant)
- **Framework**: Ultralytics YOLOv8, PyTorch 2.0+
- **Input Resolution**: 640x640 pixels
- **Inference Format**: ONNX Runtime for production deployment
- **Performance Target**: <35ms inference time per frame on GPU

#### Detection Classes (30+ categories)

**Recyclables:**
- Plastic bottles (PET, HDPE)
- Plastic containers
- Glass bottles
- Glass jars
- Aluminum cans
- Steel cans
- Paper (clean)
- Cardboard boxes
- Newspapers
- Magazines

**Organic Waste:**
- Food scraps
- Fruit peels
- Vegetable waste
- Coffee grounds
- Tea bags

**E-Waste:**
- Batteries (AA, AAA, button cells)
- Small electronics
- Circuit boards

**Textiles:**
- Clothing
- Fabric scraps

**Hazardous:**
- Chemical containers
- Paint cans
- Aerosol cans

**Non-Recyclable:**
- Contaminated packaging
- Mixed material items
- Styrofoam
- Plastic bags

#### Training Data
- **Dataset 1**: Waste Classification Data V2 (Kaggle) - 25,000+ images, 3 classes
- **Dataset 2**: Garbage Classification V2 (Kaggle) - 19,762 images, 10 classes
- **Total Training Images**: 44,762 labeled images
- **Augmentation**: Rotation (±15°), brightness (±20%), contrast adjustment, horizontal flip

#### Performance Metrics
- **mAP@0.5**: >90% (target: 92%)
- **mAP@0.5:0.95**: >75%
- **Precision**: >93%
- **Recall**: >90%
- **F1 Score**: >91%
- **FPS**: 30 frames/second (real-time)

### Implementation Details

#### File Structure
```
detection/
├── models/
│   ├── yolov8m_waste.pt          # Trained PyTorch model
│   ├── yolov8m_waste.onnx        # ONNX exported model
│   └── class_mapping.yaml        # Class ID to name mapping
├── detection_engine.py           # Main detection module
├── config.py                     # Model configuration
└── utils/
    ├── preprocessing.py          # Image preprocessing
    └── postprocessing.py         # NMS, confidence filtering
```

#### Key Components

**1. Detection Engine (`detection_engine.py`)**
```python
class WasteDetectionEngine:
    """
    Real-time waste detection using YOLOv8
    """
    def __init__(self, model_path, confidence_threshold=0.75):
        # Load ONNX model for inference
        # Initialize OpenCV video capture
        # Set up preprocessing pipeline
        
    def detect_frame(self, frame):
        # Preprocess frame (resize, normalize)
        # Run YOLO inference
        # Apply NMS (Non-Maximum Suppression)
        # Filter by confidence threshold
        # Return detections with bounding boxes
        
    def process_video_stream(self):
        # Capture frame from camera
        # Run detection
        # Render bounding boxes
        # Send results to backend API
```

**2. Preprocessing Pipeline**
- Resize to 640x640 (letterbox padding to maintain aspect ratio)
- Normalize pixel values to [0, 1]
- Convert BGR to RGB color space
- Batch preparation for GPU inference

**3. Post-processing**
- Non-Maximum Suppression (IoU threshold: 0.45)
- Confidence filtering (threshold: 0.75 default, adaptive)
- Bounding box coordinate denormalization
- Class label mapping

### Camera Integration

#### Supported Inputs
- USB webcam (720p, 1080p)
- IP camera (RTSP stream)
- Raspberry Pi Camera Module
- Pre-recorded video files (for testing)

#### Configuration
```yaml
camera:
  source: 0                    # 0 for default webcam, RTSP URL for IP cam
  resolution: [1920, 1080]     # Capture resolution
  fps: 30                      # Target frame rate
  
detection:
  input_size: [640, 640]       # Model input size
  confidence_threshold: 0.75   # Minimum confidence score
  nms_threshold: 0.45          # NMS IoU threshold
```

### Performance Optimization

#### GPU Acceleration
- CUDA support for NVIDIA GPUs (RTX 3060, 4060, etc.)
- ONNX Runtime with TensorRT execution provider
- Batch processing for multi-frame inference

#### Edge Deployment
- **Raspberry Pi 4**: INT8 quantization, 10-15 FPS achievable
- **Jetson Nano**: FP16 precision, 20-25 FPS achievable
- **Jetson Xavier NX**: FP32 precision, 30+ FPS achievable

---

## Feature 2: Dual-Agent Intelligent Routing System

### Overview
Two-stage decision engine that cross-validates classification results to detect contamination and determine optimal bin routing with 84% contamination detection rate.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│             YOLOv8 Detection Results                      │
│  Object: "Plastic Bottle", Confidence: 0.92              │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼─────────┐      ┌───────▼──────────┐
│  Material Agent │      │  Routing Agent   │
│                 │      │                  │
│  Classification:│      │  Assessment:     │
│  • Plastic      │      │  • Recyclable?   │
│  • Metal        │      │  • Contaminated? │
│  • Paper        │      │  • Hazardous?    │
│  • Glass        │      │                  │
│  • Organic      │      │                  │
└───────┬─────────┘      └───────┬──────────┘
        │                         │
        └────────────┬────────────┘
                     │
            ┌────────▼─────────┐
            │ Conflict Checker │
            │                  │
            │ Agent1 vs Agent2 │
            └────────┬─────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────┐          ┌──────▼────────┐
│   Match:     │          │  Conflict:    │
│ Route to bin │          │ Manual review │
└──────────────┘          └───────────────┘
```

### Agent 1: Material Classifier

#### Purpose
Map detected object classes to fundamental material types for processing determination.

#### Classification Logic

**Input**: YOLO class label (e.g., "plastic_bottle", "aluminum_can")  
**Output**: Material type (Plastic, Metal, Paper, Glass, Organic, E-waste, Textile)

**Mapping Rules:**
```python
MATERIAL_MAPPING = {
    # Plastics
    'plastic_bottle': 'PLASTIC',
    'plastic_container': 'PLASTIC',
    'plastic_bag': 'PLASTIC',
    
    # Metals
    'aluminum_can': 'METAL',
    'steel_can': 'METAL',
    'metal_scrap': 'METAL',
    
    # Paper products
    'cardboard': 'PAPER',
    'newspaper': 'PAPER',
    'magazine': 'PAPER',
    'office_paper': 'PAPER',
    
    # Glass
    'glass_bottle': 'GLASS',
    'glass_jar': 'GLASS',
    
    # Organic
    'food_scrap': 'ORGANIC',
    'fruit_peel': 'ORGANIC',
    'vegetable_waste': 'ORGANIC',
    
    # E-waste
    'battery': 'E_WASTE',
    'electronics': 'E_WASTE',
    
    # Textiles
    'clothing': 'TEXTILE',
    'fabric': 'TEXTILE'
}
```

### Agent 2: Recyclability Assessor

#### Purpose
Evaluate whether detected item should be routed to recycling based on contamination risk, material condition, and facility capabilities.

#### Decision Tree Logic

```
Is material type recyclable? (Plastic/Metal/Paper/Glass)
│
├─ YES → Check contamination indicators
│   │
│   ├─ Food residue detected? (visual analysis)
│   │   ├─ YES → Route to LANDFILL (contaminated)
│   │   └─ NO → Continue
│   │
│   ├─ Mixed materials? (e.g., plastic+metal composite)
│   │   ├─ YES → Route to LANDFILL
│   │   └─ NO → Continue
│   │
│   ├─ Confidence < threshold?
│   │   ├─ YES → Flag for MANUAL_REVIEW
│   │   └─ NO → Route to RECYCLABLE
│   │
│   └─ Route to RECYCLABLE
│
└─ NO → Check if hazardous
    │
    ├─ Battery/Chemical/E-waste?
    │   └─ Route to HAZARDOUS
    │
    └─ Organic waste?
        ├─ YES → Route to ORGANIC
        └─ NO → Route to LANDFILL
```

#### Contamination Detection Rules

**Visual Indicators:**
1. **Food Residue**: Detected organic matter on recyclable packaging
2. **Liquid Content**: Partially filled bottles or containers
3. **Mixed Materials**: Items with multiple material types (e.g., juice carton with plastic spout)
4. **Degraded Condition**: Torn paper, crushed containers beyond recognition

**Confidence-Based Rules:**
- If detection confidence < 0.60: Flag for manual review
- If material type confidence < 0.70: Route to landfill (too uncertain)
- If agent conflict detected: Automatic manual review

### Conflict Resolution Module

#### Conflict Detection
**Agent 1** says: "This is recyclable plastic"  
**Agent 2** says: "This has contamination, send to landfill"  
→ **Conflict detected!**

#### Resolution Strategy

```python
def resolve_conflict(material_agent_decision, routing_agent_decision):
    """
    Cross-validate agent decisions and resolve conflicts
    """
    if material_agent_decision == routing_agent_decision:
        # Agents agree - high confidence decision
        return routing_agent_decision, confidence="HIGH"
    
    else:
        # Conflict detected
        contamination_score = calculate_contamination_risk()
        
        if contamination_score > 0.7:
            # High contamination risk - trust routing agent
            return "LANDFILL", confidence="MEDIUM"
        
        elif contamination_score > 0.4:
            # Uncertain - flag for human review
            return "MANUAL_REVIEW", confidence="LOW"
        
        else:
            # Low contamination risk - trust material classification
            return material_agent_decision, confidence="MEDIUM"
```

#### Conflict Logging
All conflicts are logged to database for pattern analysis and system improvement.

**Database Schema:**
```sql
CREATE TABLE agent_conflicts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    object_class VARCHAR(50),
    material_agent_decision VARCHAR(20),
    routing_agent_decision VARCHAR(20),
    final_decision VARCHAR(20),
    confidence_score FLOAT,
    contamination_score FLOAT,
    image_snapshot BYTEA
);
```

### Routing Outputs

#### Four Bin Categories

**1. RECYCLABLE** (Clean materials for processing)
- Clean plastic containers
- Glass bottles/jars
- Metal cans
- Paper/cardboard (dry, uncontaminated)
- Expected: 40-50% of total waste stream

**2. ORGANIC** (Compostable materials)
- Food scraps
- Fruit/vegetable peels
- Coffee grounds, tea bags
- Paper towels (food-soiled, but compostable)
- Expected: 30-35% of total waste stream

**3. LANDFILL** (Non-recyclable/contaminated)
- Contaminated recyclables
- Mixed material items
- Non-recyclable plastics (film, styrofoam)
- Heavily soiled items
- Expected: 15-20% of total waste stream

**4. HAZARDOUS** (Special handling required)
- Batteries (all types)
- Electronics
- Chemical containers
- Medical waste
- Expected: 5-10% of total waste stream

### Implementation Files

```
dual_agent/
├── dual_agent.py              # Main agent orchestration
├── material_agent.py          # Material classification logic
├── routing_agent.py           # Recyclability assessment logic
├── conflict_resolver.py       # Conflict detection and resolution
├── config/
│   ├── material_mapping.yaml  # YOLO class to material mapping
│   └── routing_rules.yaml     # Decision tree rules
└── utils/
    └── contamination_analyzer.py  # Visual contamination detection
```

### Performance Metrics

- **Agent Agreement Rate**: 84% (agents agree on routing)
- **Conflict Detection Rate**: 16% (conflicts identified)
- **False Positive Rate**: <8% (items incorrectly flagged)
- **Contamination Prevention**: 84% of contaminated items caught before batching

---

## Feature 3: Contamination Prevention Module

### Overview
Predictive alert system that identifies contamination patterns and generates real-time warnings to prevent batch rejection scenarios.

### Statistical Analysis Engine

#### Rolling Window Analytics

**Purpose**: Monitor contamination trends in real-time using sliding time windows.

**Window Sizes:**
- **Short-term**: Last 100 items (immediate pattern detection)
- **Medium-term**: Last 1 hour (operational trends)
- **Long-term**: Last 24 hours (daily patterns)

**Metrics Tracked:**
```python
class ContaminationMetrics:
    def __init__(self):
        self.total_items = 0
        self.contaminated_items = 0
        self.agent_conflicts = 0
        self.low_confidence_detections = 0
        self.material_breakdown = {}  # Count by material type
        self.timestamp = datetime.now()
    
    def contamination_rate(self):
        return (self.contaminated_items / self.total_items) * 100
    
    def conflict_rate(self):
        return (self.agent_conflicts / self.total_items) * 100
    
    def material_distribution(self):
        return self.material_breakdown
```

### Alert Generation System

#### Trigger Conditions

**Level 1: INFO** (Informational alerts)
- Contamination rate increases by 5% in last 100 items
- New material type detected (not seen in last hour)
- System running smoothly, no action required

**Level 2: WARNING** (Attention required)
- Contamination rate >15% in rolling 100-item window
- Agent conflict rate >20% for specific material type
- Repeated low-confidence detections (<0.70) for same category
- Manual review queue exceeds 20 items

**Level 3: CRITICAL** (Immediate action required)
- Contamination rate >25% in rolling 100-item window
- Contamination rate doubled compared to 24h average
- Hazardous item detected in wrong stream (e.g., battery in recyclables)
- System confidence dropping below 50% for extended period

#### Alert Message Format

```json
{
  "alert_id": "ALERT_2026021101234",
  "timestamp": "2026-02-11T14:23:45Z",
  "severity": "WARNING",
  "category": "CONTAMINATION_SPIKE",
  "message": "Plastic contamination increased from 12% to 28% in last 100 items",
  "details": {
    "material_type": "PLASTIC",
    "previous_rate": 12.0,
    "current_rate": 28.0,
    "window_size": 100,
    "recommendation": "Inspect plastic sorting mechanism and review recent items"
  },
  "actions": [
    "Enable secondary inspection for plastic items",
    "Review last 50 plastic routing decisions",
    "Check camera angle and lighting conditions"
  ]
}
```

### Trend Analysis

#### Contamination Pattern Detection

**Pattern 1: Gradual Increase**
- Contamination rate slowly climbing over hours
- Indicates: Equipment degradation, lighting changes, or operator fatigue
- Action: Schedule maintenance, adjust thresholds

**Pattern 2: Sudden Spike**
- Sharp contamination increase in short window
- Indicates: New waste source, system misconfiguration, or camera obstruction
- Action: Immediate investigation, pause operations if critical

**Pattern 3: Periodic Fluctuation**
- Contamination varies with time of day
- Indicates: Different waste sources at different times (cafeteria lunch rush, office end-of-day)
- Action: Adjust thresholds based on time of day

**Pattern 4: Material-Specific**
- One material type consistently problematic
- Indicates: Model training issue, specific contamination source
- Action: Retrain model on that category, investigate source

#### Time-Series Analysis

```python
def analyze_contamination_trend(window_hours=24):
    """
    Analyze contamination rate trends over time
    """
    # Query hourly contamination rates
    hourly_data = get_hourly_metrics(window_hours)
    
    # Calculate statistics
    mean_rate = np.mean(hourly_data)
    std_dev = np.std(hourly_data)
    current_rate = hourly_data[-1]
    
    # Detect anomalies (>2 standard deviations)
    if current_rate > (mean_rate + 2 * std_dev):
        severity = "CRITICAL"
        message = f"Contamination rate {current_rate:.1f}% is significantly higher than normal ({mean_rate:.1f}%)"
        
    elif current_rate > (mean_rate + std_dev):
        severity = "WARNING"
        message = f"Contamination rate {current_rate:.1f}% is elevated above average ({mean_rate:.1f}%)"
    
    else:
        severity = "INFO"
        message = f"Contamination rate {current_rate:.1f}% within normal range"
    
    return {
        'severity': severity,
        'message': message,
        'current_rate': current_rate,
        'average_rate': mean_rate,
        'std_deviation': std_dev
    }
```

### Database Schema

```sql
-- Detection events table
CREATE TABLE detection_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    object_class VARCHAR(50),
    material_type VARCHAR(20),
    confidence_score FLOAT,
    routing_decision VARCHAR(20),
    contaminated BOOLEAN,
    agent_conflict BOOLEAN
);

-- Contamination alerts table
CREATE TABLE contamination_alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    severity VARCHAR(10),  -- INFO, WARNING, CRITICAL
    category VARCHAR(50),  -- CONTAMINATION_SPIKE, CONFLICT_RATE, etc.
    message TEXT,
    details JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(50),
    acknowledged_at TIMESTAMP
);

-- System metrics table (time-series)
CREATE TABLE system_metrics (
    timestamp TIMESTAMP PRIMARY KEY,
    total_items INTEGER,
    contaminated_items INTEGER,
    contamination_rate FLOAT,
    agent_conflicts INTEGER,
    conflict_rate FLOAT,
    avg_confidence FLOAT,
    material_breakdown JSONB
);

-- Create hypertable for time-series data (TimescaleDB)
SELECT create_hypertable('system_metrics', 'timestamp');
```

### WebSocket Alert Streaming

#### Real-Time Notification Flow

```
Detection Event
      │
      ▼
Contamination Checker
      │
      ├─ Normal → Continue
      │
      └─ Alert Triggered
             │
             ▼
      Alert Generator
             │
             ▼
      WebSocket Broadcast
             │
             ▼
      Dashboard (Toast Notification)
```

#### WebSocket Implementation

**Backend (FastAPI):**
```python
from fastapi import WebSocket

class AlertManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def broadcast_alert(self, alert: dict):
        for connection in self.active_connections:
            await connection.send_json(alert)

alert_manager = AlertManager()

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await alert_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        alert_manager.active_connections.remove(websocket)
```

**Frontend (React):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts');

ws.onmessage = (event) => {
    const alert = JSON.parse(event.data);
    
    // Show toast notification
    showToast({
        severity: alert.severity,
        message: alert.message,
        duration: alert.severity === 'CRITICAL' ? 0 : 5000  // Critical alerts stay until dismissed
    });
};
```

### Preventive Action Recommendations

#### Automated Responses

Based on alert severity and type, system can automatically:

**For Contamination Spikes:**
1. Increase confidence threshold temporarily (+0.10)
2. Enable secondary verification for affected material type
3. Trigger manual review for next 50 items of that type

**For Agent Conflicts:**
1. Log all conflicts for later analysis
2. Route conflicted items to manual review queue
3. Adjust decision weights if pattern emerges

**For Low Confidence Detections:**
1. Reduce processing speed to improve detection quality
2. Request camera adjustment or cleaning
3. Switch to backup model if available

### Implementation Files

```
contamination/
├── contamination_detector.py     # Main detection logic
├── alert_generator.py            # Alert creation and formatting
├── trend_analyzer.py             # Statistical analysis
├── websocket_manager.py          # Real-time alert streaming
└── config/
    ├── alert_thresholds.yaml     # Configurable alert triggers
    └── response_actions.yaml     # Automated response rules
```

---

## Feature 4: Environmental & Economic Impact Dashboard

### Overview
Real-time quantification of CO₂ emissions saved and material recovery value based on routing decisions and contamination prevention.

### CO₂ Savings Calculation Model

#### Emission Factors (kg CO₂ saved per kg material recycled)

Based on EPA and IPCC data for avoided emissions through recycling vs. landfill/virgin production:

**Recyclable Materials:**
- **Plastic**: 1.5 kg CO₂/kg (avoided oil extraction and plastic manufacturing)
- **Paper/Cardboard**: 0.9 kg CO₂/kg (avoided deforestation and paper production)
- **Metal (Aluminum)**: 9.0 kg CO₂/kg (avoided bauxite mining and smelting)
- **Metal (Steel)**: 1.5 kg CO₂/kg (avoided iron ore mining and processing)
- **Glass**: 0.5 kg CO₂/kg (avoided sand mining and high-temp melting)

**Organic Composting:**
- **Food Waste**: 0.3 kg CO₂/kg (avoided methane from landfill decomposition)

**Contamination Prevention Bonus:**
- Each contaminated batch prevented saves ~1,000 items worth of CO₂
- Average contaminated batch loss: 25 kg recyclables × 1.5 avg CO₂ factor = 37.5 kg CO₂

#### Calculation Implementation

```python
class CO2Calculator:
    """
    Calculate CO₂ savings from waste routing decisions
    """
    
    EMISSION_FACTORS = {
        'PLASTIC': 1.5,
        'PAPER': 0.9,
        'METAL_ALUMINUM': 9.0,
        'METAL_STEEL': 1.5,
        'GLASS': 0.5,
        'ORGANIC': 0.3
    }
    
    AVERAGE_WEIGHTS = {
        # Average weight per item in kg
        'plastic_bottle': 0.015,
        'plastic_container': 0.050,
        'aluminum_can': 0.015,
        'steel_can': 0.030,
        'glass_bottle': 0.300,
        'cardboard': 0.100,
        'newspaper': 0.050,
        'food_scrap': 0.150
    }
    
    def calculate_item_co2_savings(self, object_class, routing_decision):
        """
        Calculate CO₂ saved for single item
        """
        if routing_decision not in ['RECYCLABLE', 'ORGANIC']:
            return 0  # No savings for landfill/hazardous
        
        # Get material type and weight
        material = self.get_material_type(object_class)
        weight_kg = self.AVERAGE_WEIGHTS.get(object_class, 0.05)  # Default 50g
        
        # Calculate savings
        emission_factor = self.EMISSION_FACTORS.get(material, 0)
        co2_saved = weight_kg * emission_factor
        
        return co2_saved
    
    def calculate_batch_prevention_bonus(self, contamination_prevented):
        """
        Calculate CO₂ saved by preventing contaminated batches
        """
        # Each prevented contamination saves ~1000 items from rejection
        avg_batch_weight = 25  # kg
        avg_emission_factor = 1.5  # weighted average
        
        return contamination_prevented * avg_batch_weight * avg_emission_factor
    
    def get_total_co2_savings(self, start_date, end_date):
        """
        Query database for total CO₂ saved in date range
        """
        events = query_detection_events(start_date, end_date)
        
        total_savings = 0
        for event in events:
            total_savings += self.calculate_item_co2_savings(
                event.object_class, 
                event.routing_decision
            )
        
        # Add contamination prevention bonus
        contaminations_prevented = count_prevented_contaminations(start_date, end_date)
        total_savings += self.calculate_batch_prevention_bonus(contaminations_prevented)
        
        return total_savings
```

### Revenue Recovery Model

#### Material Market Values (USD per kg)

Based on 2025 recycled material commodity prices:

**Recyclable Materials:**
- **Clean PET Plastic**: $0.40/kg
- **Clean HDPE Plastic**: $0.35/kg
- **Mixed Plastic**: $0.15/kg (lower quality)
- **Aluminum**: $0.80/kg
- **Steel/Tin**: $0.10/kg
- **Clean Cardboard**: $0.08/kg
- **Mixed Paper**: $0.05/kg
- **Clear Glass**: $0.05/kg
- **Mixed Glass**: $0.02/kg

**Contamination Cost:**
- **Rejected Batch**: -$50/batch (sorting labor + disposal fees)
- **Contaminated Material**: -$0.10/kg (cleaning/disposal cost)

#### Calculation Implementation

```python
class RevenueEstimator:
    """
    Estimate economic value from material recovery
    """
    
    MATERIAL_VALUES = {
        'PLASTIC_PET': 0.40,
        'PLASTIC_HDPE': 0.35,
        'PLASTIC_MIXED': 0.15,
        'METAL_ALUMINUM': 0.80,
        'METAL_STEEL': 0.10,
        'PAPER_CARDBOARD': 0.08,
        'PAPER_MIXED': 0.05,
        'GLASS_CLEAR': 0.05,
        'GLASS_MIXED': 0.02
    }
    
    CONTAMINATION_COST = {
        'rejected_batch': -50.00,
        'contaminated_material': -0.10
    }
    
    def calculate_item_value(self, object_class, routing_decision, contaminated=False):
        """
        Calculate economic value for single item
        """
        if routing_decision != 'RECYCLABLE' or contaminated:
            return 0
        
        # Get material category and weight
        material_category = self.map_to_value_category(object_class)
        weight_kg = CO2Calculator.AVERAGE_WEIGHTS.get(object_class, 0.05)
        
        # Calculate value
        unit_value = self.MATERIAL_VALUES.get(material_category, 0)
        item_value = weight_kg * unit_value
        
        return item_value
    
    def calculate_contamination_cost_avoided(self, contaminations_prevented):
        """
        Calculate cost savings from preventing contaminated batches
        """
        return contaminations_prevented * abs(self.CONTAMINATION_COST['rejected_batch'])
    
    def get_total_revenue_recovery(self, start_date, end_date):
        """
        Calculate total estimated revenue from material recovery
        """
        events = query_detection_events(start_date, end_date)
        
        total_revenue = 0
        for event in events:
            total_revenue += self.calculate_item_value(
                event.object_class,
                event.routing_decision,
                event.contaminated
            )
        
        # Add contamination prevention savings
        contaminations_prevented = count_prevented_contaminations(start_date, end_date)
        total_revenue += self.calculate_contamination_cost_avoided(contaminations_prevented)
        
        return total_revenue
```

### Dashboard Metrics & Visualizations

#### Real-Time Metrics Panel

**Key Performance Indicators (KPIs):**

```
┌────────────────────────────────────────────────────────┐
│  REAL-TIME SYSTEM METRICS                             │
├────────────────────────────────────────────────────────┤
│                                                        │
│  📊 Total Items Processed Today: 2,847                │
│  ✅ Recycling Rate: 48.3%                             │
│  ⚠️  Contamination Rate: 8.2%                         │
│  🌍 CO₂ Saved Today: 42.5 kg                          │
│  💰 Revenue Recovered: $156.80                        │
│  ⏱️  Average Processing Time: 118ms/item              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

#### Visualization Components

**1. Material Composition Breakdown (Pie Chart)**
```javascript
{
  type: 'pie',
  data: {
    labels: ['Plastic', 'Paper', 'Metal', 'Glass', 'Organic', 'Landfill', 'Hazardous'],
    datasets: [{
      data: [32, 18, 12, 8, 24, 4, 2],  // Percentages
      backgroundColor: ['#3B82F6', '#10B981', '#6B7280', '#06B6D4', '#84CC16', '#EF4444', '#F59E0B']
    }]
  }
}
```

**2. Contamination Trend (Line Chart)**
```javascript
{
  type: 'line',
  data: {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],  // Time of day
    datasets: [
      {
        label: 'Contamination Rate (%)',
        data: [5.2, 4.8, 9.1, 12.3, 8.7, 6.4],
        borderColor: '#EF4444',
        fill: false
      },
      {
        label: 'Target Rate (%)',
        data: [10, 10, 10, 10, 10, 10],
        borderColor: '#10B981',
        borderDash: [5, 5],
        fill: false
      }
    ]
  }
}
```

**3. CO₂ Savings Progress (Bar Chart)**
```javascript
{
  type: 'bar',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'CO₂ Saved (kg)',
      data: [38.2, 42.1, 45.7, 41.3, 48.9, 35.4, 31.2],
      backgroundColor: '#10B981'
    }]
  }
}
```

**4. Revenue Recovery (Stacked Bar Chart)**
```javascript
{
  type: 'bar',
  data: {
    labels: ['Plastic', 'Metal', 'Paper', 'Glass'],
    datasets: [
      {
        label: 'Material Value',
        data: [85.40, 48.20, 12.60, 3.80],
        backgroundColor: '#3B82F6'
      },
      {
        label: 'Contamination Savings',
        data: [15.00, 8.00, 3.00, 1.00],
        backgroundColor: '#10B981'
      }
    ]
  },
  options: {
    scales: {
      x: { stacked: true },
      y: { stacked: true }
    }
  }
}
```

**5. Routing Decision Stream (Real-Time Feed)**
```
┌─────────────────────────────────────────────────┐
│  RECENT ROUTING DECISIONS                       │
├─────────────────────────────────────────────────┤
│  14:23:45  Plastic Bottle  → ♻️  Recyclable    │
│  14:23:44  Food Scrap      → 🌱 Organic        │
│  14:23:43  Aluminum Can    → ♻️  Recyclable    │
│  14:23:42  Battery         → ⚠️  Hazardous     │
│  14:23:40  Plastic Bag     → 🗑️  Landfill      │
│  14:23:38  Glass Bottle    → ♻️  Recyclable    │
└─────────────────────────────────────────────────┘
```

#### Historical Analytics Dashboard

**Weekly/Monthly Summary Tables:**
```sql
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_items,
    SUM(CASE WHEN routing_decision = 'RECYCLABLE' THEN 1 ELSE 0 END) as recyclable_count,
    AVG(contamination_rate) as avg_contamination,
    SUM(co2_saved) as total_co2_saved,
    SUM(revenue_value) as total_revenue
FROM 
    daily_metrics
WHERE 
    timestamp >= NOW() - INTERVAL '30 days'
GROUP BY 
    DATE(timestamp)
ORDER BY 
    date DESC;
```

### Implementation Files

```
impact/
├── co2_calculator.py          # CO₂ savings calculations
├── revenue_estimator.py       # Economic value estimation
├── metrics_aggregator.py      # Database queries and aggregation
└── config/
    ├── emission_factors.yaml  # CO₂ emission factors by material
    └── material_values.yaml   # Market values for recyclables
```

---

## Feature 5: Adaptive Learning System

### Overview
Self-improving system that adjusts confidence thresholds and routing rules based on operational feedback and contamination trends.

### Threshold Adaptation Logic

#### Dynamic Confidence Adjustment

**Principle**: System confidence thresholds should adapt to observed performance to balance throughput and accuracy.

**Adjustment Triggers:**

**Scenario 1: High Contamination Rate**
- **Condition**: Contamination rate > 20% for specific material over 500 items
- **Action**: Increase confidence threshold by +0.05 (up to max 0.95)
- **Effect**: More items sent to manual review, fewer contaminations slip through
- **Duration**: Maintain increased threshold until contamination drops below 10% for 1000 items

**Scenario 2: Low Contamination Rate (High Precision)**
- **Condition**: Contamination rate < 5% for 7 consecutive days
- **Action**: Decrease confidence threshold by -0.02 (down to min 0.60)
- **Effect**: Higher throughput, fewer items needlessly sent to manual review
- **Duration**: Monitor for 2 days; revert if contamination rises above 8%

**Scenario 3: Agent Conflict Pattern**
- **Condition**: Agent conflict rate > 25% for specific material class
- **Action**: Flag material class for model retraining; route all to manual review temporarily
- **Effect**: Prevent systematic errors while model is improved
- **Duration**: Until new model deployed or rules updated

#### Implementation

```python
class AdaptiveThresholdManager:
    """
    Dynamically adjust confidence thresholds based on performance
    """
    
    def __init__(self):
        self.thresholds = {
            'PLASTIC': 0.75,
            'METAL': 0.75,
            'PAPER': 0.75,
            'GLASS': 0.75,
            'ORGANIC': 0.70
        }
        
        self.min_threshold = 0.60
        self.max_threshold = 0.95
        
        self.adjustment_history = []
    
    def analyze_performance(self, material_type, window_size=500):
        """
        Analyze recent performance for material type
        """
        recent_events = query_recent_events(material_type, window_size)
        
        contamination_rate = calculate_contamination_rate(recent_events)
        conflict_rate = calculate_conflict_rate(recent_events)
        avg_confidence = calculate_avg_confidence(recent_events)
        
        return {
            'contamination_rate': contamination_rate,
            'conflict_rate': conflict_rate,
            'avg_confidence': avg_confidence
        }
    
    def adjust_threshold(self, material_type, performance_metrics):
        """
        Adjust confidence threshold based on performance
        """
        current_threshold = self.thresholds[material_type]
        
        contamination_rate = performance_metrics['contamination_rate']
        conflict_rate = performance_metrics['conflict_rate']
        
        # High contamination - increase threshold
        if contamination_rate > 20:
            new_threshold = min(current_threshold + 0.05, self.max_threshold)
            reason = f"High contamination rate: {contamination_rate:.1f}%"
        
        # Very low contamination - decrease threshold
        elif contamination_rate < 5 and self.is_stable_low_contamination(material_type, days=7):
            new_threshold = max(current_threshold - 0.02, self.min_threshold)
            reason = f"Stable low contamination: {contamination_rate:.1f}%"
        
        # High conflict rate - flag for review
        elif conflict_rate > 25:
            new_threshold = self.max_threshold  # Maximum caution
            reason = f"High agent conflict rate: {conflict_rate:.1f}%"
        
        else:
            new_threshold = current_threshold
            reason = "No adjustment needed"
        
        # Log adjustment
        if new_threshold != current_threshold:
            self.log_adjustment(material_type, current_threshold, new_threshold, reason)
            self.thresholds[material_type] = new_threshold
        
        return new_threshold
    
    def log_adjustment(self, material_type, old_threshold, new_threshold, reason):
        """
        Log threshold changes to database
        """
        adjustment = {
            'timestamp': datetime.now(),
            'material_type': material_type,
            'old_threshold': old_threshold,
            'new_threshold': new_threshold,
            'reason': reason
        }
        
        self.adjustment_history.append(adjustment)
        save_to_database('threshold_adjustments', adjustment)
```

### Pattern Recognition

#### Recurring False Positive Detection

**Objective**: Identify systematic errors where model consistently misclassifies specific items.

**Detection Method:**
1. Track all manual review corrections
2. Group by object class and error type
3. Identify patterns with >10 occurrences in 24 hours

**Example Pattern:**
```
Object: "plastic_container"
Error: Classified as recyclable, actually contaminated (food residue)
Frequency: 15 occurrences in 24 hours
Pattern: All occurred between 12:00-14:00 (lunch time)
```

**Automated Response:**
1. Flag pattern in system logs
2. Adjust routing rules for that object class during that time window
3. Generate recommendation for model retraining
4. Alert operators to investigate root cause

#### Time-Based Pattern Analysis

**Identify performance variations by:**
- **Time of Day**: Morning vs. afternoon vs. evening
- **Day of Week**: Weekday vs. weekend patterns
- **Waste Source**: Cafeteria vs. office vs. residential

**Example SQL Query:**
```sql
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour_of_day,
    material_type,
    AVG(contamination_rate) as avg_contamination,
    COUNT(*) as item_count
FROM 
    detection_events
WHERE 
    timestamp >= NOW() - INTERVAL '7 days'
GROUP BY 
    hour_of_day, material_type
ORDER BY 
    hour_of_day, avg_contamination DESC;
```

### Feedback Loop System

#### Manual Override Logging

**Purpose**: Capture human corrections to improve future decisions.

**Process:**
1. Operator reviews item flagged for manual inspection
2. Operator makes final routing decision
3. System logs: original AI decision + operator decision + reason
4. Discrepancies added to retraining dataset

**Database Schema:**
```sql
CREATE TABLE manual_overrides (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    object_class VARCHAR(50),
    ai_decision VARCHAR(20),
    operator_decision VARCHAR(20),
    reason VARCHAR(200),
    operator_id VARCHAR(50),
    image_snapshot BYTEA
);
```

#### Retraining Data Collection

**Automatic Dataset Building:**
- All manual overrides saved with images
- Contamination false positives/negatives logged
- Agent conflicts with resolution saved

**Retraining Trigger:**
- Accumulate >1000 correction samples
- Or specific class has >100 corrections
- Or contamination rate doesn't improve after threshold adjustment

### Performance Monitoring

#### Daily Automated Reports

**Generated Every 24 Hours:**

```
═══════════════════════════════════════════════════════
  COGNIRECYCLE DAILY PERFORMANCE REPORT
  Date: 2026-02-11
═══════════════════════════════════════════════════════

OPERATIONAL METRICS:
  Total Items Processed: 3,421
  System Uptime: 23.5 hours
  Average Processing Speed: 28.7 FPS
  
ACCURACY METRICS:
  Overall Contamination Rate: 7.8%
  Agent Agreement Rate: 87.3%
  Average Detection Confidence: 0.84
  Manual Review Rate: 12.1%
  
MATERIAL BREAKDOWN:
  Plastic:   34.2% (1,170 items, 8.9% contamination)
  Paper:     19.1% (654 items, 5.2% contamination)
  Metal:     11.3% (387 items, 3.1% contamination)
  Glass:     8.7% (298 items, 4.5% contamination)
  Organic:   21.4% (732 items, 11.2% contamination)
  Landfill:  4.2% (144 items)
  Hazardous: 1.1% (36 items)

ENVIRONMENTAL IMPACT:
  CO₂ Saved: 48.7 kg
  Revenue Recovered: $187.20
  Contaminated Batches Prevented: 3
  
SYSTEM HEALTH:
  Active Alerts: 2 (both INFO level)
  Threshold Adjustments: 1 (PLASTIC: 0.75 → 0.78)
  Model Performance: Stable
  
RECOMMENDATIONS:
  ✓ System performing within targets
  ⚠ Monitor plastic contamination trend (increasing)
  → Consider cafeteria education campaign
  
═══════════════════════════════════════════════════════
```

#### Confidence Distribution Analysis

**Monitor how confident the system is in its decisions:**

```python
def analyze_confidence_distribution(date):
    """
    Analyze distribution of detection confidence scores
    """
    events = query_events_by_date(date)
    
    confidence_bins = {
        'very_high': 0,   # 0.90-1.00
        'high': 0,        # 0.80-0.90
        'medium': 0,      # 0.70-0.80
        'low': 0,         # 0.60-0.70
        'very_low': 0     # <0.60
    }
    
    for event in events:
        conf = event.confidence_score
        
        if conf >= 0.90:
            confidence_bins['very_high'] += 1
        elif conf >= 0.80:
            confidence_bins['high'] += 1
        elif conf >= 0.70:
            confidence_bins['medium'] += 1
        elif conf >= 0.60:
            confidence_bins['low'] += 1
        else:
            confidence_bins['very_low'] += 1
    
    # Ideal distribution: Most in high/very_high, few in low/very_low
    return confidence_bins
```

**Healthy Distribution:**
- Very High (>0.90): 60-70%
- High (0.80-0.90): 20-25%
- Medium (0.70-0.80): 8-12%
- Low (0.60-0.70): 2-5%
- Very Low (<0.60): <2%

### Implementation Files

```
adaptive/
├── threshold_manager.py       # Dynamic threshold adjustment
├── pattern_detector.py        # Error pattern recognition
├── feedback_collector.py      # Manual override logging
├── performance_reporter.py    # Daily report generation
└── config/
    ├── adaptation_rules.yaml  # Threshold adjustment rules
    └── report_templates/      # Report format templates
```

---

## Technology Stack

### Computer Vision & AI

```yaml
Framework: PyTorch 2.0+
Model: YOLOv8 (Ultralytics)
  - Variant: YOLOv8m (medium)
  - Input: 640x640 RGB
  - Output: 30+ object classes
  
Optimization:
  - ONNX Runtime 1.15+
  - TensorRT (for Jetson devices)
  - INT8 Quantization (edge deployment)
  
Image Processing: OpenCV 4.8+
Data Augmentation: Albumentations
```

### Backend

```yaml
Framework: FastAPI 0.104+
ASGI Server: Uvicorn
Database: PostgreSQL 15+
  - Extension: TimescaleDB (time-series)
  - ORM: SQLAlchemy 2.0
  
Real-time: WebSocket
Task Queue: Celery (for async processing)
Caching: Redis (optional, for performance)
```

### Frontend

```yaml
Framework: React 18+
Build Tool: Vite
State Management: React Context / Zustand
Charts: Chart.js 4.0+
Real-time: WebSocket API
Styling: Tailwind CSS
```

### Deployment

```yaml
Containerization: Docker
Orchestration: Docker Compose
  
Edge Devices:
  - Raspberry Pi 4 (4GB RAM min)
  - NVIDIA Jetson Nano (4GB)
  - NVIDIA Jetson Xavier NX
  
Cloud Options:
  - AWS EC2 (GPU instances)
  - Google Cloud Platform
  - Azure ML
```

### Development Tools

```yaml
Version Control: Git + GitHub
CI/CD: GitHub Actions
Code Quality:
  - Python: Black, Flake8, MyPy
  - JavaScript: ESLint, Prettier
  
Testing:
  - Python: pytest
  - JavaScript: Jest, React Testing Library
  
Documentation: Markdown + Sphinx
```

---

## Conclusion

This document outlines the complete technical implementation of all 5 core features for the CogniRecycle prototype. Each feature is designed to work together as an integrated system:

1. **Detection Engine** identifies waste objects
2. **Dual-Agent System** makes intelligent routing decisions
3. **Contamination Prevention** monitors and alerts on issues
4. **Impact Dashboard** quantifies environmental and economic value
5. **Adaptive Learning** continuously improves system performance

The modular architecture allows for independent development and testing of each component while maintaining clear integration points.

---

**Document Version:** 1.0  
**Last Updated:** February 7, 2026  
**Authors:** Sanyam Wadhwa & Pratham Garg
