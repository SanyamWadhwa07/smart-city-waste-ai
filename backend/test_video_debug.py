"""
Debug script to check detector and classifier outputs on video.
"""
import sys
import os
import cv2

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.detector import WasteDetector
from app.classifier import MaterialClassifier

def test_video(video_path):
    print("Loading models...")
    detector = WasteDetector(device="cpu", verbose=True)
    classifier = MaterialClassifier(device="cpu", verbose=True)
    
    print(f"\nDetector info: {detector.get_info()}")
    print(f"Classifier info: {classifier.get_info()}")
    
    print(f"\nOpening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Failed to open video!")
        return
    
    # Read first few frames
    for frame_num in range(5):
        ret, frame = cap.read()
        if not ret:
            break
        
        print(f"\n{'='*60}")
        print(f"Frame {frame_num + 1}")
        print('='*60)
        
        # Run detector
        detections, crops = detector.detect(frame, return_crops=True)
        
        print(f"Detected {len(detections)} objects")
        
        for i, det in enumerate(detections):
            print(f"\n  Detection {i+1}:")
            print(f"    Label: {det.label}")
            print(f"    Confidence: {det.confidence:.4f}")
            print(f"    BBox (normalized): {[f'{x:.3f}' for x in det.bbox]}")
            print(f"    BBox (absolute): {det.bbox_abs}")
            
            if crops and i < len(crops):
                crop = crops[i]
                print(f"    Crop shape: {crop.shape}")
        
        # Run classifier on crops
        if crops:
            print(f"\nRunning classifier on {len(crops)} crops...")
            classifications = classifier.classify_batch(crops, return_top_k=True)
            
            for i, cls in enumerate(classifications):
                print(f"\n  Classification {i+1}:")
                print(f"    Label: {cls.label}")
                print(f"    Confidence: {cls.confidence:.4f}")
                if cls.top_k_labels:
                    print(f"    Top-K labels: {cls.top_k_labels}")
                    print(f"    Top-K scores: {[f'{x:.4f}' for x in cls.top_k_scores]}")
    
    cap.release()
    print("\n\nDone!")

if __name__ == "__main__":
    video_path = "final.mp4"
    test_video(video_path)
