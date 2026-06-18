@echo off
title TripManager Pro GUI Startup
echo ===================================================
echo 🌍 Starting TripManager Pro System GUI...
echo ===================================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python and try again.
    pause
    exit /b
)

echo [1/3] Python found.
echo [2/3] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Dependency installation encountered issues. 
    echo Please ensure you have internet access and try again if it fails to run.
)

echo [3/3] Launching local web server...
:: Open browser in background
start http://127.0.0.1:5000

:: Run the server
python app.py
pause
