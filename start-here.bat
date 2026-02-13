@echo off
REM One-click system check and launcher for CogniRecycle

echo.
echo ============================================================
echo   CogniRecycle - One-Click Launcher
echo ============================================================
echo.

REM Run system check first
echo Running pre-flight checks...
echo.
python check_system.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo   All checks passed! Ready to launch.
    echo ============================================================
    echo.
    set /p launch="Start the dashboard now? (Y/N): "
    
    if /i "%launch%"=="Y" (
        echo.
        echo Launching dashboard...
        powershell -ExecutionPolicy Bypass -File start-dashboard.ps1
    ) else (
        echo.
        echo To start manually, run: start-dashboard.ps1
        pause
    )
) else (
    echo.
    echo ============================================================
    echo   Some checks failed. Please fix issues above.
    echo ============================================================
    echo.
    echo Common fixes:
    echo   1. Install backend: cd backend ^&^& pip install -r requirements.txt -r requirements-yolo.txt
    echo   2. Install frontend: npm install
    echo   3. Verify models: dir backend\models\*.pt
    echo.
    pause
)
