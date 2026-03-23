# ♻️ Smart City Waste AI

AI-powered waste classification system using **YOLO-based object detection**, extended with **dual-model inference for contamination detection**.

---

## 🧠 Overview

This project addresses inefficient waste segregation by using real-time computer vision to:

- Detect waste objects
- Classify material type (plastic, paper, metal, etc.)
- Identify contamination (mixed or incorrect disposal)

Built for **smart city pipelines and intelligent waste management systems**.

---

## ⚙️ Key Features

- Real-time waste detection using YOLO
- Multi-class classification on Garbage Classification Dataset 2
- Dual-model pipeline for contamination detection
- Designed for camera / smart-bin integration
- Low-latency inference pipeline

---

## 🏗️ System Architecture

Input (Image / Video)  
→ YOLO Model (Object Detection + Classification)  
→ Secondary Model (Contamination Detection)  
→ Post-processing  
→ Output (Class + Contamination Status)

---

## 🧪 Tech Stack

- Python  
- YOLO (Ultralytics)  
- OpenCV  
- NumPy  

---

## 📊 Model Details

- **Primary Model:** YOLO trained on Garbage Classification Dataset 2  
- **Task:** Object detection + waste classification  
- **Secondary Model:** Contamination detection (identifies mixed/incorrect waste)  
- **Pipeline:** Dual inference → combined decision output  

---

## 📂 Project Structure

smart-city-waste-ai/  
│  
├── data/  
├── models/  
├── src/  
├── app.py  
├── requirements.txt  
└── README.md  

---

## 🚀 Getting Started

Clone the repository:

    git clone https://github.com/SanyamWadhwa07/smart-city-waste-ai.git
    cd smart-city-waste-ai

Install dependencies:

    pip install -r requirements.txt

Run the app:

    python app.py

---

## 🎯 Use Cases

- Smart waste bins  
- Automated sorting systems  
- Recycling plants  
- Campus / city waste monitoring  

---

## 📈 Future Improvements

- Edge deployment (Jetson / mobile)  
- Real-time video stream optimization  
- Route optimization for waste collection  
- Dashboard for analytics  

---

