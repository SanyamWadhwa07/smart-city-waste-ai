"""
Comprehensive test script for CogniRecycle Dashboard Integration.

Tests:
1. Model loading and initialization
2. Dual-agent inference on test images
3. Backend API endpoints
4. WebSocket streaming
5. Full integration test

Usage:
    python test_integration.py
    python test_integration.py --backend-only
    python test_integration.py --models-only
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import cv2
    import numpy as np
    from ultralytics import YOLO
    import requests
    import websocket
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("📦 Install: pip install opencv-python ultralytics requests websocket-client")
    sys.exit(1)


class IntegrationTester:
    """Test suite for CogniRecycle system integration."""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            "models": {"passed": False, "details": {}},
            "backend": {"passed": False, "details": {}},
            "integration": {"passed": False, "details": {}}
        }
    
    def test_models(self) -> bool:
        """Test model loading and inference."""
        print("\n" + "="*60)
        print("🧪 TEST 1: Model Loading & Inference")
        print("="*60)
        
        try:
            # Check model files exist
            tier1_path = Path("../models/yolov8_tier1.pt")
            tier2_path = Path("../models/yolov8_tier2.pt")
            
            if not tier1_path.exists():
                print(f"❌ Tier 1 model not found: {tier1_path}")
                self.results["models"]["details"]["tier1"] = "File not found"
                return False
            
            if not tier2_path.exists():
                print(f"❌ Tier 2 model not found: {tier2_path}")
                self.results["models"]["details"]["tier2"] = "File not found"
                return False
            
            print(f"✅ Model files found")
            
            # Load Tier 1 model
            print("\n🔷 Loading Tier 1 model...")
            tier1_model = YOLO(str(tier1_path))
            print(f"   Classes: {tier1_model.names}")
            self.results["models"]["details"]["tier1_classes"] = len(tier1_model.names)
            
            # Load Tier 2 model
            print("\n🔶 Loading Tier 2 model...")
            tier2_model = YOLO(str(tier2_path))
            print(f"   Classes: {tier2_model.names}")
            self.results["models"]["details"]["tier2_classes"] = len(tier2_model.names)
            
            # Create a test image
            print("\n🖼️  Testing inference on synthetic image...")
            test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            # Test Tier 1
            result1 = tier1_model(test_img, verbose=False)
            print(f"   Tier 1 inference: ✅ Success")
            
            # Test Tier 2
            result2 = tier2_model(test_img, verbose=False)
            print(f"   Tier 2 inference: ✅ Success")
            
            self.results["models"]["passed"] = True
            print("\n✅ Model tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Model test failed: {e}")
            self.results["models"]["details"]["error"] = str(e)
            return False
    
    def test_backend_api(self) -> bool:
        """Test backend API endpoints."""
        print("\n" + "="*60)
        print("🧪 TEST 2: Backend API")
        print("="*60)
        
        try:
            # Test health endpoint
            print("\n🔍 Testing health endpoint...")
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Health check passed: {response.json()}")
                self.results["backend"]["details"]["health"] = "OK"
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
            
            # Test metrics endpoint
            print("\n📊 Testing metrics endpoint...")
            response = requests.get(f"{self.backend_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics = response.json()
                print(f"   ✅ Metrics: {json.dumps(metrics, indent=2)}")
                self.results["backend"]["details"]["metrics"] = metrics
            else:
                print(f"   ❌ Metrics failed: {response.status_code}")
                return False
            
            # Test impact endpoint
            print("\n🌍 Testing impact endpoint...")
            response = requests.get(f"{self.backend_url}/impact", timeout=5)
            if response.status_code == 200:
                impact = response.json()
                print(f"   ✅ Impact: CO2 saved = {impact.get('total_co2_kg', 0):.2f} kg")
                self.results["backend"]["details"]["impact"] = impact
            else:
                print(f"   ❌ Impact failed: {response.status_code}")
                return False
            
            self.results["backend"]["passed"] = True
            print("\n✅ Backend API tests passed!")
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Cannot connect to backend at {self.backend_url}")
            print("   Make sure the backend is running: cd backend && uvicorn app.main:app")
            self.results["backend"]["details"]["error"] = "Connection refused"
            return False
        except Exception as e:
            print(f"\n❌ Backend test failed: {e}")
            self.results["backend"]["details"]["error"] = str(e)
            return False
    
    def test_websocket(self, duration: int = 5) -> bool:
        """Test WebSocket streaming."""
        print("\n" + "="*60)
        print("🧪 TEST 3: WebSocket Streaming")
        print("="*60)
        
        try:
            ws_url = self.backend_url.replace("http://", "ws://") + "/ws/detections"
            print(f"\n🔗 Connecting to: {ws_url}")
            
            ws = websocket.create_connection(ws_url, timeout=5)
            print("   ✅ WebSocket connected")
            
            print(f"\n📡 Listening for {duration} seconds...")
            events_received = 0
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    ws.settimeout(1)
                    message = ws.recv()
                    data = json.loads(message)
                    events_received += 1
                    
                    if events_received == 1:
                        print(f"\n   Sample event received:")
                        print(f"   {json.dumps(data, indent=2)[:200]}...")
                    
                except websocket.WebSocketTimeoutException:
                    continue
            
            ws.close()
            
            print(f"\n✅ Received {events_received} events in {duration} seconds")
            print(f"   Rate: {events_received/duration:.2f} events/sec")
            
            self.results["integration"]["details"]["websocket_events"] = events_received
            self.results["integration"]["passed"] = events_received > 0
            
            return events_received > 0
            
        except Exception as e:
            print(f"\n❌ WebSocket test failed: {e}")
            self.results["integration"]["details"]["error"] = str(e)
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        total_tests = 3
        passed_tests = sum([
            self.results["models"]["passed"],
            self.results["backend"]["passed"],
            self.results["integration"]["passed"]
        ])
        
        print(f"\n✅ Models: {'PASSED' if self.results['models']['passed'] else '❌ FAILED'}")
        print(f"✅ Backend API: {'PASSED' if self.results['backend']['passed'] else '❌ FAILED'}")
        print(f"✅ Integration: {'PASSED' if self.results['integration']['passed'] else '❌ FAILED'}")
        
        print(f"\n{'='*60}")
        print(f"Result: {passed_tests}/{total_tests} tests passed")
        print(f"{'='*60}")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! System is ready for production.")
            return True
        else:
            print("\n⚠️  Some tests failed. Check details above.")
            return False


def main():
    parser = argparse.ArgumentParser(description="Test CogniRecycle Integration")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--models-only", action="store_true", help="Test models only")
    parser.add_argument("--backend-only", action="store_true", help="Test backend only")
    parser.add_argument("--ws-duration", type=int, default=5, help="WebSocket test duration (seconds)")
    args = parser.parse_args()
    
    tester = IntegrationTester(args.backend_url)
    
    print("\n🚀 CogniRecycle Integration Test Suite")
    print(f"Backend: {args.backend_url}")
    
    success = True
    
    # Test models
    if not args.backend_only:
        if not tester.test_models():
            success = False
            if args.models_only:
                return 1
    
    # Test backend
    if not args.models_only:
        if not tester.test_backend_api():
            success = False
        else:
            # Test WebSocket only if backend is working
            if not tester.test_websocket(args.ws_duration):
                success = False
    
    # Print summary
    if tester.print_summary():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
