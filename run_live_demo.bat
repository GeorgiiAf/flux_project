@echo off
REM Live Demo - Shows vehicle detection in real-time

echo ========================================
echo Vehicle Detection - Live Demo
echo ========================================
echo.
echo This will show the video processing with
echo bounding boxes drawn around detected vehicles
echo.
echo Controls:
echo   - Press 'q' to quit
echo   - Press 'p' to pause/resume
echo   - Press 's' to save current frame
echo.
echo Starting demo...
echo.

python src\live_demo.py data\videos\Clip1_morning.mp4

echo.
pause
