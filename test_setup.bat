@echo off
REM Test if the system is set up correctly

echo ========================================
echo Testing Vehicle Compliance Monitor Setup
echo ========================================
echo.

echo Testing Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.

echo Testing package imports...
python test_imports.py
if errorlevel 1 (
    echo.
    echo ERROR: Some packages are missing!
    echo Please run: python -m pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

echo Testing main script...
python src\main.py --help
if errorlevel 1 (
    echo ERROR: Main script failed!
    pause
    exit /b 1
)
echo.

echo ========================================
echo SUCCESS! System is ready to use
echo ========================================
echo.
echo To process your videos, run: run_system.bat
echo Or use: python src\main.py --video data\videos\Clip1_morning.mp4
echo.

pause
