@echo off
REM Script to upload Vehicle Compliance Monitor to GitHub

echo =========================================
echo Upload to GitHub - Vehicle Compliance Monitor
echo =========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Git is installed
echo.

REM Check if already initialized
if exist .git (
    echo Git repository already initialized
    echo.
) else (
    echo Initializing Git repository...
    git init
    echo Git initialized
    echo.
)

REM Add all files
echo Adding files to git...
git add .
echo Files added
echo.

REM Create commit
echo Creating commit...
git commit -m "Initial commit: Vehicle Compliance Monitor - Complete AI-powered vehicle compliance monitoring system - YOLO-based vehicle detection - License plate OCR - Compliance database checking - Traffic analytics - Google Colab notebook - Comprehensive documentation"
echo Commit created
echo.

REM Instructions
echo =========================================
echo Next Steps:
echo =========================================
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository named: vehicle-compliance-monitor
echo 3. DON'T initialize with README
echo 4. After creating, run these commands:
echo.
echo    git remote add origin https://github.com/YOUR-USERNAME/vehicle-compliance-monitor.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Replace YOUR-USERNAME with your GitHub username
echo.
echo =========================================
echo Ready to push to GitHub!
echo =========================================
echo.

pause
