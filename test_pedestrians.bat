@echo off
REM Quick test to verify pedestrian detection

echo ========================================
echo Testing Pedestrian Detection
echo ========================================
echo.
echo This will process one video with pedestrian detection enabled
echo.

python src/main.py --video data/videos/Clip1_morning.mp4 --output outputs/test_pedestrians --fps 3

echo.
echo Check outputs/test_pedestrians/ for results
echo Look for "person" in the object counts
echo.
pause
