"""
Pre-flight check for CogniRecycle Dashboard.
Verifies all dependencies and configuration before launch.
"""

import os
import sys
from pathlib import Path

# Color output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.RESET}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (Need 3.8+)")
        return False

def check_models():
    """Check if trained models exist."""
    models_dir = Path("backend/models")
    tier1 = models_dir / "yolov8_tier1.pt"
    tier2 = models_dir / "yolov8_tier2.pt"
    
    all_exist = True
    
    if tier1.exists():
        size_mb = tier1.stat().st_size / (1024 * 1024)
        print_success(f"Tier 1 model found ({size_mb:.1f} MB)")
    else:
        print_error("Tier 1 model NOT found: backend/models/yolov8_tier1.pt")
        all_exist = False
    
    if tier2.exists():
        size_mb = tier2.stat().st_size / (1024 * 1024)
        print_success(f"Tier 2 model found ({size_mb:.1f} MB)")
    else:
        print_error("Tier 2 model NOT found: backend/models/yolov8_tier2.pt")
        all_exist = False
    
    return all_exist

def check_backend_dependencies():
    """Check backend Python dependencies."""
    required = [
        ('fastapi', 'FastAPI web framework'),
        ('uvicorn', 'ASGI server'),
        ('ultralytics', 'YOLO inference'),
        ('cv2', 'OpenCV (as cv2)'),
        ('numpy', 'NumPy'),
    ]
    
    all_installed = True
    
    for module_name, description in required:
        try:
            __import__(module_name)
            print_success(f"{description}")
        except ImportError:
            print_error(f"{description} NOT installed")
            all_installed = False
    
    return all_installed

def check_frontend_dependencies():
    """Check if Node.js and npm are available."""
    import subprocess
    
    all_good = True
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"Node.js {version}")
        else:
            print_error("Node.js check failed")
            all_good = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_error("Node.js NOT found")
        all_good = False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"npm {version}")
        else:
            print_error("npm check failed")
            all_good = False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_error("npm NOT found")
        all_good = False
    
    # Check node_modules
    if Path("node_modules").exists():
        print_success("Frontend dependencies installed")
    else:
        print_warning("Frontend dependencies NOT installed (run: npm install)")
        all_good = False
    
    return all_good

def check_environment():
    """Check environment configuration."""
    backend_env = Path("backend/.env")
    
    if backend_env.exists():
        print_success("Backend .env file exists")
        
        # Check key variables
        with open(backend_env, 'r') as f:
            content = f.read()
            
        if 'USE_REAL_INFERENCE=1' in content:
            print_success("Real-time inference enabled")
        else:
            print_warning("Real-time inference not enabled in .env")
        
        if 'TIER1_MODEL_PATH' in content and 'TIER2_MODEL_PATH' in content:
            print_success("Model paths configured")
        else:
            print_warning("Model paths not fully configured")
        
        return True
    else:
        print_warning("Backend .env file NOT found (will use defaults)")
        return False

def check_camera():
    """Quick camera availability check."""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        is_open = cap.isOpened()
        cap.release()
        
        if is_open:
            print_success("Default camera accessible")
            return True
        else:
            print_warning("Default camera not accessible (you can still use video files)")
            return False
    except Exception as e:
        print_warning(f"Camera check failed: {e}")
        return False

def print_next_steps(all_checks_passed):
    """Print recommended next steps."""
    print_header("🚀 Next Steps")
    
    if all_checks_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ System is ready to launch!{Colors.RESET}\n")
        print("To start the dashboard:")
        print(f"  {Colors.CYAN}.\\start-dashboard.ps1{Colors.RESET}")
        print("\nTo run tests:")
        print(f"  {Colors.CYAN}.\\test-dashboard.ps1{Colors.RESET}")
        print("\nTo test with camera:")
        print(f"  {Colors.CYAN}cd backend\\training{Colors.RESET}")
        print(f"  {Colors.CYAN}python test_system.py --source 0{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️  Some checks failed. Please fix issues above.{Colors.RESET}\n")
        print("Common fixes:")
        print(f"  {Colors.CYAN}# Install backend dependencies:{Colors.RESET}")
        print(f"  {Colors.CYAN}cd backend{Colors.RESET}")
        print(f"  {Colors.CYAN}pip install -r requirements.txt -r requirements-yolo.txt{Colors.RESET}")
        print(f"\n  {Colors.CYAN}# Install frontend dependencies:{Colors.RESET}")
        print(f"  {Colors.CYAN}npm install{Colors.RESET}")
        print(f"\n  {Colors.cyan}# Verify models exist:{Colors.RESET}")
        print(f"  {Colors.CYAN}ls backend\\models\\*.pt{Colors.RESET}")

def main():
    print_header("🔍 CogniRecycle Pre-flight Check")
    
    checks = []
    
    # Python version
    print_info("Checking Python version...")
    checks.append(('Python', check_python_version()))
    
    # Models
    print_info("\nChecking trained models...")
    checks.append(('Models', check_models()))
    
    # Backend dependencies
    print_info("\nChecking backend dependencies...")
    checks.append(('Backend Deps', check_backend_dependencies()))
    
    # Frontend
    print_info("\nChecking frontend setup...")
    checks.append(('Frontend', check_frontend_dependencies()))
    
    # Environment
    print_info("\nChecking environment configuration...")
    checks.append(('Environment', check_environment()))
    
    # Camera
    print_info("\nChecking camera availability...")
    checks.append(('Camera', check_camera()))
    
    # Summary
    print_header("📋 Summary")
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{name:15} {status}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.RESET}")
    
    all_critical_passed = all(result for name, result in checks if name in ['Python', 'Models', 'Backend Deps'])
    
    print_next_steps(all_critical_passed)
    
    return 0 if all_critical_passed else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
        sys.exit(1)
