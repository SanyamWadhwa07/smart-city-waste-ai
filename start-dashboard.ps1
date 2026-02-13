#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start CogniRecycle Dashboard with Real-time Inference

.DESCRIPTION
    This script starts both the backend API with real-time model inference
    and the frontend dashboard in development mode.

.PARAMETER Mode
    Run mode: 'both' (default), 'backend', or 'frontend'

.PARAMETER Production
    Run frontend in production mode

.EXAMPLE
    .\start-dashboard.ps1
    Start both backend and frontend in development mode

.EXAMPLE
    .\start-dashboard.ps1 -Mode backend
    Start only the backend

.EXAMPLE
    .\start-dashboard.ps1 -Production
    Start with production frontend build
#>

param(
    [ValidateSet('both', 'backend', 'frontend')]
    [string]$Mode = 'both',
    
    [switch]$Production
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

# Banner
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "🚀 CogniRecycle Dashboard Startup" -ForegroundColor Cyan
Write-Host ("="*60) -ForegroundColor Cyan

# Check if virtual environment exists
$venvPath = "venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Warning "Virtual environment not found. Creating..."
    python -m venv venv
    Write-Success "✅ Virtual environment created"
}

# Function to start backend
function Start-Backend {
    Write-Info "`n🔷 Starting Backend API..."
    
    # Activate virtual environment and start backend
    Push-Location backend
    
    # Check if dependencies are installed
    Write-Info "📦 Checking backend dependencies..."
    & ..\venv\Scripts\python.exe -c "import fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Installing backend dependencies..."
        & ..\venv\Scripts\pip.exe install -r requirements.txt
        & ..\venv\Scripts\pip.exe install -r requirements-yolo.txt
        Write-Success "✅ Dependencies installed"
    }
    
    # Check if detector model exists
    if (-not (Test-Path "models\yolov8m-seg.pt")) {
        Write-Error "❌ Detector model not found: models\yolov8m-seg.pt"
        Write-Warning "Please ensure the segmentation model is in backend\models\"
        Pop-Location
        exit 1
    }
    
    Write-Success "✅ Detector model found (yolov8m-seg.pt)"
    Write-Info "📦 Classifier will be downloaded from Hugging Face on first run"
    
    # Load environment variables
    if (Test-Path ".env") {
        Write-Info "📄 Loading environment from .env"
        Get-Content .env | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$') {
                $name = $matches[1]
                $value = $matches[2]
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
    
    # Set required environment variables
    $env:USE_REAL_INFERENCE = "1"
    $env:TIER1_MODEL_PATH = "models/yolov8m-seg.pt"
    $env:TIER2_MODEL_PATH = "prithivMLmods/Augmented-Waste-Classifier-SigLIP2"
    
    Write-Success "✅ Environment configured for real-time inference"
    Write-Info "`nStarting Uvicorn server..."
    Write-Info "Backend will be available at: http://localhost:8000"
    Write-Info "API docs at: http://localhost:8000/docs"
    Write-Info "`nPress Ctrl+C to stop`n"
    
    & ..\venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
    
    Pop-Location
}

# Function to start frontend
function Start-Frontend {
    Write-Info "`n🔶 Starting Frontend Dashboard..."
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Warning "Node modules not found. Installing..."
        npm install
        Write-Success "✅ Dependencies installed"
    }
    
    if ($Production) {
        Write-Info "Building for production..."
        npm run build
        Write-Info "Starting preview server..."
        Write-Info "Frontend will be available at: http://localhost:4173"
        npm run preview
    } else {
        Write-Info "Starting development server..."
        Write-Info "Frontend will be available at: http://localhost:5173"
        Write-Info "`nPress Ctrl+C to stop`n"
        npm run dev
    }
}

# Main execution
try {
    switch ($Mode) {
        'backend' {
            Start-Backend
        }
        'frontend' {
            Start-Frontend
        }
        'both' {
            Write-Info "`n📋 Starting both backend and frontend..."
            Write-Warning "`nNote: Both services will run in this terminal."
            Write-Warning "For separate terminals, run:"
            Write-Warning "  Terminal 1: .\start-dashboard.ps1 -Mode backend"
            Write-Warning "  Terminal 2: .\start-dashboard.ps1 -Mode frontend"
            
            # Start backend in background job
            Write-Info "`nStarting backend in background..."
            $backendJob = Start-Job -ScriptBlock {
                param($scriptPath)
                & $scriptPath -Mode backend
            } -ArgumentList $PSCommandPath
            
            Start-Sleep -Seconds 5
            
            # Check if backend started successfully
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 2 -ErrorAction Stop
                Write-Success "✅ Backend started successfully"
            } catch {
                Write-Error "❌ Backend failed to start"
                Stop-Job $backendJob
                Remove-Job $backendJob
                exit 1
            }
            
            # Start frontend in foreground
            Start-Frontend
            
            # Cleanup on exit
            Stop-Job $backendJob
            Remove-Job $backendJob
        }
    }
} catch {
    Write-Error "`n❌ Error: $_"
    exit 1
}

Write-Success "`n✅ Shutdown complete"
