"""
Test pipeline step by step to find where confidence is lost.
"""
import sys
import os
import cv2

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.detector import WasteDetector
from app.classifier import MaterialClassifier
from app.decision import DecisionEngine
from app.pipeline import DualAgentPipeline

def test_pipeline_step_by_step(video_path):
    print("="*60)
    print("DETAILED PIPELINE DEBUG")
    print("="*60)
    
    # Create components
    detector = WasteDetector(device="cpu", verbose=False)
    classifier = MaterialClassifier(device="cpu", verbose=False)
    decision_engine = DecisionEngine()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Failed to open video!")
        return
    
    # Skip to frame 3 which had detection in our debug test
    for _ in range(2):
        cap.read()
    
    ret, frame = cap.read()
    if not ret:
        print("Failed")
        return
    
    print(f"\nFrame shape: {frame.shape}")
    print("\n" + "="*60)
    print("STEP 1: DETECTION")
    print("="*60)
    
    detections, crops = detector.detect(frame, return_crops=True)
    print(f"Number of detections: {len(detections)}")
    
    for i, det in enumerate(detections):
        print(f"\nDetection {i+1}:")
        print(f"  label: {det.label}")
        print(f"  confidence: {det.confidence}")
        print(f"  bbox: {det.bbox}")
        print(f"  bbox_abs: {det.bbox_abs}")
    
    if not detections:
        print("No detections, stopping")
        return
    
    print("\n" + "="*60)
    print("STEP 2: CLASSIFICATION")
    print("="*60)
    
    classifications = classifier.classify_batch(crops, return_top_k=True)
    print(f"Number of classifications: {len(classifications)}")
    
    for i, cls in enumerate(classifications):
        print(f"\nClassification {i+1}:")
        print(f"  label: {cls.label}")
        print(f"  confidence: {cls.confidence}")
        if cls.top_k_labels:
            print(f"  top_k_labels: {cls.top_k_labels}")
            print(f"  top_k_scores: {cls.top_k_scores}")
    
    print("\n" + "="*60)
    print("STEP 3: DECISION")
    print("="*60)
    
    decisions = decision_engine.batch_decide(detections, classifications)
    print(f"Number of decisions: {len(decisions)}")
    
    for i, dec in enumerate(decisions):
        print(f"\nDecision {i+1}:")
        print(f"  detector_label: {dec.detector_label}")
        print(f"  classifier_label: {dec.classifier_label}")
        print(f"  detector_material: {dec.detector_material}")
        print(f"  classifier_material: {dec.classifier_material}")
        print(f"  confidence_detector: {dec.confidence_detector}")
        print(f"  confidence_classifier: {dec.confidence_classifier}")
        print(f"  final_material: {dec.final_material}")
        print(f"  decision_type: {dec.decision_type}")
        print(f"  confidence_score: {dec.confidence_score}")
    
    print("\n" + "="*60)
    print("STEP 4: FULL PIPELINE")
    print("="*60)
    
    # Reset video
    cap.set(cv2.CAP_PROP_POS_FRAMES, 2)
    ret, frame = cap.read()
    
    pipeline = DualAgentPipeline(
        detector=detector,
        classifier=classifier,
        verbose=False
    )
    
    result = pipeline.analyze_frame(frame, frame_id="test_frame")
    result_dict = result.to_dict()
    
    print(f"Number of objects: {result_dict['total_objects']}")
    
    for i, obj in enumerate(result_dict['objects']):
        print(f"\nPipeline Object {i+1}:")
        for key, value in obj.items():
            print(f"  {key}: {value}")
    
    cap.release()
    print("\nDone!")

if __name__ == "__main__":
    video_path = "final.mp4"
    test_pipeline_step_by_step(video_path)
