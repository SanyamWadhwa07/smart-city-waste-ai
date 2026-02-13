"""
Real-time Waste Detection System - Webcam Test
Tests the full dual-agent pipeline with live webcam feed.

Usage:
    python test_realtime_webcam.py [--source CAMERA_ID] [--device cpu|cuda] [--save-video]

Examples:
    python test_realtime_webcam.py                    # Default webcam (camera 0)
    python test_realtime_webcam.py --source 1         # Use camera 1
    python test_realtime_webcam.py --device cuda      # Use GPU
    python test_realtime_webcam.py --save-video       # Save detection video

Controls:
    - Press 'q' or ESC to quit
    - Press 's' to save current frame
    - Press 'p' to pause/unpause
    - Press 'h' to toggle help overlay
"""

import sys
import os
import argparse
import time
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.pipeline import DualAgentPipeline
from app.detector import WasteDetector
from app.classifier import MaterialClassifier


class RealtimeWasteDetector:
    """Real-time waste detection with webcam."""
    
    def __init__(
        self,
        camera_id = 0,
        device: str = "auto",
        save_video: bool = False,
        output_dir: str = "output"
    ):
        """
        Initialize realtime detector.
        
        Args:
            camera_id: Camera device ID or video file path
            device: Processing device (cpu, cuda, auto)
            save_video: Whether to save video output
            output_dir: Directory for saved outputs
        """
        self.camera_id = camera_id
        self.device = device
        self.save_video = save_video
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # State
        self.paused = False
        self.show_help = True
        self.frame_count = 0
        self.detection_count = 0
        
        # Stats
        self.fps = 0
        self.processing_time = 0
        
        # Video writer
        self.video_writer = None
        
        print("=" * 70)
        print("REAL-TIME WASTE DETECTION SYSTEM")
        print("=" * 70)
        print()
        
        # Initialize pipeline
        print("Loading AI models (this may take a moment)...")
        
        # Create detector with explicit device setting (disable FP16 for stability)
        detector = WasteDetector(
            device=device if device != "auto" else "cpu",
            half=False,
            verbose=False
        )
        
        # Create classifier with explicit device setting
        classifier = MaterialClassifier(
            device=device if device != "auto" else "cpu",
            verbose=False
        )
        
        self.pipeline = DualAgentPipeline(
            detector=detector,
            classifier=classifier,
            camera_source=None,  # We'll manage camera separately
            encode_frames=False,  # Don't need to encode for display
            verbose=False
        )
        
        print(f"✓ Pipeline initialized")
        detector_info = self.pipeline.detector.get_info()
        classifier_info = self.pipeline.classifier.get_info()
        print(f"  - Detector: {detector_info['model_path']}")
        print(f"  - Classifier: {classifier_info['model_path']}")
        print(f"  - Device: {detector_info['device']}")
        print()
        
        # Open camera or video
        source_type = "video file" if isinstance(camera_id, str) else f"camera {camera_id}"
        print(f"Opening {source_type}...")
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open {source_type}")
        
        # Get camera/video properties
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.camera_fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        print(f"✓ {source_type.capitalize()} opened: {self.frame_width}x{self.frame_height} @ {self.camera_fps:.1f} FPS")
        print()
        
        # Setup video writer if requested
        if save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_path = self.output_dir / f"detection_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(video_path),
                fourcc,
                20.0,  # Output FPS
                (self.frame_width, self.frame_height)
            )
            print(f"✓ Recording to: {video_path}")
            print()
    
    def draw_overlay(self, frame: np.ndarray, analysis_result: dict = None) -> np.ndarray:
        """Draw UI overlay on frame."""
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Semi-transparent status bar at top
        cv2.rectangle(overlay, (0, 0), (w, 120), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)
        
        # Title
        cv2.putText(
            frame, "Smart Waste Detection System",
            (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2
        )
        
        # Stats
        stats_y = 60
        cv2.putText(
            frame, f"FPS: {self.fps:.1f}  |  Processing: {self.processing_time:.0f}ms  |  Frames: {self.frame_count}",
            (10, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
        )
        
        # Detection info
        if analysis_result:
            objects = analysis_result.get('objects', [])
            stats_y += 25
            cv2.putText(
                frame, f"Objects Detected: {len(objects)}  |  Total Detections: {self.detection_count}",
                (10, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
            )
            
            # Show detected objects summary
            if objects:
                materials = {}
                for obj in objects:
                    mat = obj.get('material', 'unknown')
                    materials[mat] = materials.get(mat, 0) + 1
                
                summary = "  |  ".join([f"{mat}: {cnt}" for mat, cnt in materials.items()])
                stats_y += 25
                cv2.putText(
                    frame, summary[:100],  # Truncate if too long
                    (10, stats_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1
                )
        
        # Help overlay
        if self.show_help:
            help_y = h - 120
            cv2.rectangle(frame, (0, help_y), (w, h), (0, 0, 0), -1)
            
            help_texts = [
                "Controls: [Q]uit | [P]ause | [S]ave Frame | [H]ide Help",
            ]
            
            for i, text in enumerate(help_texts):
                cv2.putText(
                    frame, text,
                    (10, help_y + 30 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                )
        
        # Paused indicator
        if self.paused:
            cv2.putText(
                frame, "PAUSED",
                (w // 2 - 60, h // 2),
                cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 3
            )
        
        return frame
    
    def draw_detections(self, frame: np.ndarray, analysis_result: dict) -> np.ndarray:
        """Draw bounding boxes and labels for detected objects."""
        if not analysis_result:
            return frame
        
        if 'objects' not in analysis_result or not analysis_result['objects']:
            return frame
        
        frame_h, frame_w = frame.shape[:2]
        
        for obj in analysis_result['objects']:
            # Get normalized bbox and convert to absolute coordinates
            bbox_norm = obj.get('bbox')
            if not bbox_norm or len(bbox_norm) < 4:
                continue
            
            # Convert normalized [x, y, w, h] to absolute pixels
            x = int(bbox_norm[0] * frame_w)
            y = int(bbox_norm[1] * frame_h)
            w = int(bbox_norm[2] * frame_w)
            h = int(bbox_norm[3] * frame_h)
            
            # Get confidence scores
            detector_conf = obj.get('confidence_detector', 0.0)
            classifier_conf = obj.get('confidence_classifier', 0.0)
            confidence = max(detector_conf, classifier_conf)
            
            # Color based on confidence
            if confidence > 0.7:
                color = (0, 255, 0)  # Green - high confidence
            elif confidence > 0.5:
                color = (0, 255, 255)  # Yellow - medium confidence
            else:
                color = (0, 165, 255)  # Orange - low confidence
            
            # Draw box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Get label information
            material = obj.get('final_material', 'unknown')
            bin_type = obj.get('recommended_bin', 'unknown')
            
            label = f"{material} -> {bin_type}"
            conf_text = f"{confidence:.2f}"
            
            # Label background
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            cv2.rectangle(
                frame,
                (x, y - label_h - 25),
                (x + label_w + 80, y),
                color,
                -1
            )
            
            # Label text
            cv2.putText(
                frame, label,
                (x + 5, y - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
            )
            cv2.putText(
                frame, conf_text,
                (x + 5, y - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1
            )
        
        return frame
    
    def save_frame(self, frame: np.ndarray, analysis_result: dict = None):
        """Save current frame with detection results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        # Save raw frame
        frame_path = self.output_dir / f"frame_{timestamp}.jpg"
        cv2.imwrite(str(frame_path), frame)
        
        # Save analysis result
        if analysis_result:
            import json
            result_path = self.output_dir / f"result_{timestamp}.json"
            with open(result_path, 'w') as f:
                json.dump(analysis_result, f, indent=2)
        
        print(f"✓ Saved: {frame_path.name}")
    
    def run(self):
        """Run real-time detection loop."""
        print("=" * 70)
        print("STARTING DETECTION...")
        print("=" * 70)
        print()
        
        cv2.namedWindow('Waste Detection', cv2.WINDOW_NORMAL)
        
        last_time = time.time()
        
        try:
            while True:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                self.frame_count += 1
                
                # Process frame if not paused
                analysis_result = None
                if not self.paused:
                    start_time = time.time()
                    
                    try:
                        analysis_result = self.pipeline.analyze_frame(frame)
                        
                        # Convert to dict if it's an AnalysisResult object
                        if analysis_result and hasattr(analysis_result, 'to_dict'):
                            analysis_result = analysis_result.to_dict()
                        
                        # Log detection results
                        if analysis_result and 'objects' in analysis_result:
                            objects = analysis_result['objects']
                            if objects:
                                print(f"\n[Frame {self.frame_count}] Detected {len(objects)} object(s):")
                                for i, obj in enumerate(objects, 1):
                                    # Debug: print all available keys
                                    print(f"  Object {i} keys: {list(obj.keys())}")
                                    
                                    # Get field values with correct field names
                                    detector_label = obj.get('detector_label', 'unknown')
                                    detector_conf = obj.get('confidence_detector', 0.0)
                                    
                                    classifier_label = obj.get('classifier_label', 'unknown')
                                    classifier_conf = obj.get('confidence_classifier', 0.0)
                                    
                                    final_material = obj.get('final_material', 'unknown')
                                    
                                    # Calculate final confidence (max of detector and classifier)
                                    final_conf = max(detector_conf, classifier_conf)
                                    
                                    # Get bin destination
                                    bin_dest = obj.get('recommended_bin', 'unknown')
                                    
                                    print(f"    Detector: {detector_label} ({detector_conf:.2f})")
                                    print(f"    Classifier: {classifier_label} ({classifier_conf:.2f})")
                                    print(f"    Final Material: {final_material}")
                                    print(f"    Final Confidence: {final_conf:.2f}")
                                    print(f"    Bin: {bin_dest}")
                            
                            # Update stats
                            self.detection_count += len(objects)
                    
                    except Exception as e:
                        print(f"\n[Frame {self.frame_count}] Error during analysis: {e}")
                        import traceback
                        traceback.print_exc()
                        analysis_result = None
                    
                    self.processing_time = (time.time() - start_time) * 1000
                
                # Draw detections
                if analysis_result:
                    frame = self.draw_detections(frame, analysis_result)
                
                # Draw overlay
                frame = self.draw_overlay(frame, analysis_result)
                
                # Calculate FPS
                current_time = time.time()
                self.fps = 1.0 / (current_time - last_time) if (current_time - last_time) > 0 else 0
                last_time = current_time
                
                # Show frame
                cv2.imshow('Waste Detection', frame)
                
                # Save video frame
                if self.video_writer is not None:
                    self.video_writer.write(frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # Q or ESC
                    print("Stopping detection...")
                    break
                elif key == ord('p'):  # Pause
                    self.paused = not self.paused
                    print(f"{'Paused' if self.paused else 'Resumed'}")
                elif key == ord('s'):  # Save frame
                    self.save_frame(frame, analysis_result)
                elif key == ord('h'):  # Toggle help
                    self.show_help = not self.show_help
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        
        if self.cap is not None:
            self.cap.release()
        
        if self.video_writer is not None:
            self.video_writer.release()
            print("✓ Video saved")
        
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 70)
        print("SESSION SUMMARY")
        print("=" * 70)
        print(f"Total Frames: {self.frame_count}")
        print(f"Total Detections: {self.detection_count}")
        print(f"Average FPS: {self.fps:.1f}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Real-time waste detection with webcam",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--source', '-s',
        default=0,
        help='Camera device ID (default: 0) or path to video file'
    )
    
    parser.add_argument(
        '--device', '-d',
        type=str,
        default='auto',
        choices=['cpu', 'cuda', 'auto'],
        help='Processing device (default: auto)'
    )
    
    parser.add_argument(
        '--save-video',
        action='store_true',
        help='Save detection video to output directory'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='output',
        help='Output directory for saved frames/videos (default: output)'
    )
    
    args = parser.parse_args()
    
    # Convert source to int if it's a digit, otherwise keep as string (video path)
    source = args.source
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    
    try:
        detector = RealtimeWasteDetector(
            camera_id=source,
            device=args.device,
            save_video=args.save_video,
            output_dir=args.output_dir
        )
        detector.run()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
