@echo off
echo ===============================================
echo    Advanced Medical Visualization Tool
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "app.py" (
    echo ERROR: app.py not found
    echo Please run this script from the web directory
    pause
    exit /b 1
)

echo Starting the Medical Visualization Tool...
echo.
echo The application will open in your default web browser
echo If it doesn't open automatically, navigate to: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo ===============================================
echo.

REM Run the Python application
python run_app.py

pause
