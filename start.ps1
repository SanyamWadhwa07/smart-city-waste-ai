# Start Full System - Backend + Frontend

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting Dual-Agent Waste Sorting System" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if models exist
$tier1 = "backend\models\yolov8_tier1.pt"
$tier2 = "backend\models\yolov8_tier2.pt"

if (-not (Test-Path $tier1) -or -not (Test-Path $tier2)) {
    Write-Host "⚠ Warning: Trained models not found!" -ForegroundColor Yellow
    Write-Host "Will run in SIMULATOR mode (no real detection)`n" -ForegroundColor Yellow
    $env:USE_REAL_INFERENCE = "0"
} else {
    Write-Host "✓ Found trained models" -ForegroundColor Green
    Write-Host "  - $tier1" -ForegroundColor Gray
    Write-Host "  - $tier2`n" -ForegroundColor Gray
}

Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:5173`n" -ForegroundColor Gray

# Start backend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Write-Host '🔷 Starting Backend...' -ForegroundColor Blue
    cd '$PWD\backend'
    if (Test-Path ..\venv\Scripts\Activate.ps1) {
        & ..\venv\Scripts\Activate.ps1
    }
    python -m app.main
"@

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "`n🔶 Starting Frontend...`n" -ForegroundColor Magenta
npm run dev
