@echo off
REM Vehicle Compliance Monitor - Run Script
REM This script processes your videos through the complete pipeline

echo ========================================
echo Vehicle Compliance Monitor
echo ========================================
echo.

REM Check if videos exist
if not exist "data\videos\Clip1_morning.mp4" (
    echo ERROR: Clip1_morning.mp4 not found in data\videos\
    echo Please ensure your videos are in the data\videos\ directory
    pause
    exit /b 1
)

if not exist "data\videos\Clip2_day.mp4" (
    echo ERROR: Clip2_day.mp4 not found in data\videos\
    echo Please ensure your videos are in the data\videos\ directory
    pause
    exit /b 1
)

echo Videos found:
echo   - Clip1_morning.mp4
echo   - Clip2_day.mp4
echo.

echo Starting processing...
echo This may take 10-20 minutes depending on your hardware
echo.

REM Run the pipeline
python src\main.py --video data\videos\Clip1_morning.mp4 data\videos\Clip2_day.mp4

echo.
echo ========================================
echo Processing Complete!
echo ========================================
echo.
echo Check the outputs\ directory for results:
echo   - Violation reports (CSV, JSON, TXT)
echo   - Analytics visualizations (PNG)
echo   - Time profiles and heatmaps
echo   - Video comparison
echo.

pause
