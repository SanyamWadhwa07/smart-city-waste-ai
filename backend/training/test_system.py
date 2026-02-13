"""
Test dual-agent system with real-time detection.

Tests both models together and shows agreement/disagreement.

Usage:
    # Test with webcam (real-time)
    python test_system.py --source 0
    
    # Test with image
    python test_system.py --source path/to/image.jpg
    
    # Test with video
    python test_system.py --source path/to/video.mp4
"""

import argparse
import cv2
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ultralytics import YOLO


# Cross-validation mapping
TIER2_TO_TIER1_MAPPING = {
    "plastic": "PLASTIC",
    "glass": "GLASS",
    "metal": "METAL",
    "paper": "PAPER",
    "cardboard": "CARDBOARD",
    "biological": "BIODEGRADABLE",
    "battery": "HAZARDOUS",
    "trash": "LANDFILL",
    "clothes": "LANDFILL",
    "shoes": "LANDFILL",
}


def check_agreement(detector_class, classifier_class):
    """Check if agents agree."""
    expected_detector = TIER2_TO_TIER1_MAPPING.get(classifier_class.lower())
    
    if expected_detector is None:
        return False, "Unknown class"
    
    if detector_class.upper() == expected_detector:
        return True, "Agreement"
    else:
        return False, f"Contamination: {detector_class} != {expected_detector}"


def main():
    parser = argparse.ArgumentParser(description="Test dual-agent waste sorting system")
    parser.add_argument("--source", default="0", help="Source: 0 (webcam), image.jpg, video.mp4")
    parser.add_argument("--detector", default="../models/yolov8_tier1.pt", help="Primary detector model (Tier 1)")
    parser.add_argument("--classifier", default="../models/yolov8_tier2.pt", help="Secondary classifier model (Tier 2)")
    parser.add_argument("--conf", type=float, default=0.35, help="Confidence threshold")
    parser.add_argument("--save", action="store_true", help="Save output video")
    parser.add_argument("--output", default="test_output.mp4", help="Output video filename")
    args = parser.parse_args()
    
    # Load models
    print("\n🔷 Loading Primary Detector (Agent A)...")
    detector = YOLO(args.detector)
    print(f"   Classes: {detector.names}")
    
    print("\n🔶 Loading Secondary Classifier (Agent B)...")
    classifier = YOLO(args.classifier)
    print(f"   Classes: {classifier.names}")
    
    # Setup video source
    if args.source == "0":
        source = 0
        print("\n📹 Opening webcam...")
    else:
        source = args.source
        print(f"\n📹 Opening: {source}")
    
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print("❌ Failed to open video source")
        return
    
    # Setup video writer if saving
    writer = None
    if args.save:
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        print(f"💾 Saving output to: {args.output}")
    
    print("\n" + "="*60)
    print("🚀 DUAL-AGENT SYSTEM ACTIVE")
    print("="*60)
    print("Press 'q' to quit\n")
    
    frame_count = 0
    agreement_count = 0
    contamination_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Run detector (Agent A)
        detector_results = detector(frame, conf=args.conf, verbose=False)
        
        # Process detections
        for det in detector_results[0].boxes:
            x1, y1, x2, y2 = map(int, det.xyxy[0])
            conf = float(det.conf[0])
            cls_id = int(det.cls[0])
            detector_class = detector.names[cls_id]
            
            # Filter out very large boxes (likely background/person, not waste objects)
            box_area = (x2 - x1) * (y2 - y1)
            frame_area = frame.shape[0] * frame.shape[1]
            if box_area > frame_area * 0.5:  # Ignore detections larger than 50% of frame
                continue
            
            # Filter out very small boxes
            if box_area < 1000:  # Min 1000 pixels
                continue
            
            # Crop region for classifier
            crop = frame[y1:y2, x1:x2]
            
            if crop.size == 0:
                continue
            
            # Run classifier (Agent B)
            classifier_results = classifier(crop, verbose=False)
            
            if len(classifier_results) > 0 and classifier_results[0].probs is not None:
                classifier_cls_id = classifier_results[0].probs.top1
                classifier_conf = float(classifier_results[0].probs.top1conf)
                classifier_class = classifier.names[classifier_cls_id]
                
                # Check agreement
                agree, reason = check_agreement(detector_class, classifier_class)
                
                # Update statistics
                if agree:
                    agreement_count += 1
                else:
                    contamination_count += 1
                
                # Draw bounding box
                if agree:
                    color = (0, 255, 0)  # Green = Agreement
                    status = "✓ AGREE"
                else:
                    color = (0, 0, 255)  # Red = Disagreement
                    status = "✗ CONTAMINATION"
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw labels
                label1 = f"A: {detector_class} ({conf:.2f})"
                label2 = f"B: {classifier_class} ({classifier_conf:.2f})"
                label3 = f"{status}"
                
                cv2.putText(frame, label1, (x1, y1-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, label2, (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, label3, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Console output
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"Frame {frame_count}: {status}")
                    print(f"  Agent A (Detector): {detector_class} ({conf:.2f})")
                    print(f"  Agent B (Classifier): {classifier_class} ({classifier_conf:.2f})")
                    print(f"  Reason: {reason}\n")
        
        # Add statistics overlay
        stats_text = f"Frame: {frame_count} | Agreements: {agreement_count} | Contamination: {contamination_count}"
        cv2.putText(frame, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display
        cv2.imshow("Dual-Agent Waste Sorting System", frame)
        
        # Save frame if recording
        if writer is not None:
            writer.write(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    if writer is not None:
        writer.release()
        print(f"\n💾 Video saved to: {args.output}")
    cv2.destroyAllWindows()
    
    # Print final statistics
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Total Frames Processed: {frame_count}")
    print(f"Agent Agreements: {agreement_count}")
    print(f"Contamination Detected: {contamination_count}")
    if agreement_count + contamination_count > 0:
        accuracy = (agreement_count / (agreement_count + contamination_count)) * 100
        print(f"Agreement Rate: {accuracy:.2f}%")
    print("\n✅ Test complete")


if __name__ == "__main__":
    main()
