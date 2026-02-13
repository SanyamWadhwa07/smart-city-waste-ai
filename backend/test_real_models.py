"""
Test with real models (detector and classifier).
Requires models to be downloaded.
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_detector_only():
    """Test detector with real model."""
    print("=" * 60)
    print("TEST: Real Detector Loading")
    print("=" * 60 + "\n")
    
    try:
        from app.detector import WasteDetector
        from app.utils import create_dummy_frame
        
        print("Loading detector model...")
        detector = WasteDetector(
            model_path="models/yolov8m-seg.pt",
            confidence_threshold=0.40,
            device="cpu",
            verbose=True
        )
        
        print(f"✓ Detector loaded: {detector.get_info()}\n")
        
        # Test detection on dummy frame
        print("Running detection on dummy frame...")
        frame = create_dummy_frame(640, 640)
        
        detections, crops = detector.detect(frame, return_crops=True)
        
        print(f"✓ Detection complete!")
        print(f"  - Objects detected: {len(detections)}")
        
        if detections:
            print(f"\n  Detections:")
            for i, det in enumerate(detections[:5]):  # Show first 5
                print(f"    {i+1}. {det.label} (conf: {det.confidence:.2f})")
                print(f"       BBox: {det.bbox}")
        else:
            print(f"  (No objects detected in random noise - this is expected)")
        
        if crops:
            print(f"\n  - Crops extracted: {len(crops)}")
        
        print("\n✅ DETECTOR TEST PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ DETECTOR TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_classifier_only():
    """Test classifier with real model."""
    print("=" * 60)
    print("TEST: Real Classifier Loading")
    print("=" * 60 + "\n")
    
    try:
        from app.classifier import MaterialClassifier
        import numpy as np
        
        print("Loading classifier model...")
        classifier = MaterialClassifier(
            model_path="prithivMLmods/Augmented-Waste-Classifier-SigLIP2",
            device="cpu",
            batch_size=4,
            verbose=True
        )
        
        print(f"✓ Classifier loaded: {classifier.get_info()}\n")
        
        # Create dummy crops
        print("Creating test crops...")
        crops = [
            np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        print("Running classification...")
        results = classifier.classify_batch(crops, return_top_k=True)
        
        print(f"✓ Classification complete!")
        print(f"\n  Results:")
        for i, result in enumerate(results):
            print(f"    Crop {i+1}: {result.label} (conf: {result.confidence:.2f})")
            if result.top_k_labels:
                print(f"       Top-3: {', '.join(result.top_k_labels[:3])}")
        
        print("\n✅ CLASSIFIER TEST PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ CLASSIFIER TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test full pipeline with real models."""
    print("=" * 60)
    print("TEST: Full Pipeline with Real Models")
    print("=" * 60 + "\n")
    
    try:
        from app.pipeline import DualAgentPipeline
        from app.utils import create_dummy_frame
        
        print("Initializing full pipeline with real models...")
        print("(This may take a moment for model downloads...)\n")
        
        pipeline = DualAgentPipeline(
            camera_source=None,
            encode_frames=False,
            verbose=False
        )
        
        print("✓ Pipeline initialized\n")
        print(f"Pipeline info:")
        info = pipeline.get_info()
        print(f"  - Detector: {info['detector']['model_path']}")
        print(f"  - Classifier: {info['classifier']['model_path']}")
        print(f"  - Device: {info['detector']['device']}")
        print()
        
        # Test with dummy frame
        print("Analyzing test frame...")
        frame = create_dummy_frame(640, 640)
        
        result = pipeline.analyze_frame(frame)
        
        print(f"✓ Frame analyzed!")
        print(f"  - Processing time: {result.processing_time_ms:.1f}ms")
        print(f"  - Objects detected: {result.total_objects}")
        
        if result.stage_timings:
            print(f"\n  Stage timings:")
            for stage, time_ms in result.stage_timings.items():
                print(f"    • {stage}: {time_ms:.1f}ms")
        
        if result.objects:
            print(f"\n  Objects:")
            for i, obj in enumerate(result.objects):
                print(f"    {i+1}. {obj['detector_label']} → {obj['final_material']}")
                print(f"       Route: {obj['route']} ({obj['recommended_bin']})")
                print(f"       Decision: {obj['decision']}")
        else:
            print(f"\n  (No objects in random noise - expected)")
        
        print("\n✅ FULL PIPELINE TEST PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ FULL PIPELINE TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("REAL MODEL TESTS")
    print("=" * 60 + "\n")
    
    print("NOTE: Tests use random noise images, so detections are expected")
    print("to be minimal or zero. This tests model loading and inference flow.\n")
    
    results = []
    
    # Test detector
    results.append(("Detector", test_detector_only()))
    
    # Test classifier
    results.append(("Classifier", test_classifier_only()))
    
    # Test full pipeline
    results.append(("Full Pipeline", test_full_pipeline()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("  1. Test with real image: python test_real_image.py path/to/image.jpg")
        print("  2. Start backend server: cd backend && uvicorn app.main:app")
        print("  3. Test WebSocket: Connect frontend dashboard")
        print()
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
