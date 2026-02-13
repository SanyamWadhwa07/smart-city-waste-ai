@echo off
REM Quick launcher for CogniRecycle Dashboard
REM For Windows users who prefer batch files

echo.
echo ============================================================
echo   CogniRecycle Dashboard Launcher
echo ============================================================
echo.
echo Select an option:
echo.
echo   1. Start Full Dashboard (Backend + Frontend)
echo   2. Start Backend Only
echo   3. Start Frontend Only
echo   4. Run Tests (All)
echo   5. Test Models Only
echo   6. Test with Camera
echo   7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo.
    echo Starting full dashboard...
    powershell -ExecutionPolicy Bypass -File start-dashboard.ps1
) else if "%choice%"=="2" (
    echo.
    echo Starting backend only...
    powershell -ExecutionPolicy Bypass -File start-dashboard.ps1 -Mode backend
) else if "%choice%"=="3" (
    echo.
    echo Starting frontend only...
    powershell -ExecutionPolicy Bypass -File start-dashboard.ps1 -Mode frontend
) else if "%choice%"=="4" (
    echo.
    echo Running all tests...
    powershell -ExecutionPolicy Bypass -File test-dashboard.ps1
) else if "%choice%"=="5" (
    echo.
    echo Testing models only...
    powershell -ExecutionPolicy Bypass -File test-dashboard.ps1 -TestType models
) else if "%choice%"=="6" (
    echo.
    echo Testing with camera...
    powershell -ExecutionPolicy Bypass -File test-dashboard.ps1 -TestType camera
) else if "%choice%"=="7" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run again.
    pause
    exit /b 1
)

pause
