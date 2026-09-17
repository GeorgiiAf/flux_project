@echo off
REM Create submission package for AI Challenge

echo =========================================
echo Creating Challenge Submission Package
echo =========================================
echo.

REM Create a temporary directory for packaging
if exist submission_package rmdir /s /q submission_package
mkdir submission_package

echo Copying files...

REM Copy source code
xcopy /E /I /Y src submission_package\src
echo - Source code copied

REM Copy notebooks
xcopy /E /I /Y notebooks submission_package\notebooks
echo - Notebooks copied

REM Copy prompts
xcopy /E /I /Y prompts submission_package\prompts
echo - Prompts copied

REM Copy data (without videos)
mkdir submission_package\data
xcopy /E /I /Y data\*.csv submission_package\data
echo - Data files copied

REM Copy outputs (sample visualizations only)
if exist outputs (
    mkdir submission_package\outputs
    xcopy /Y outputs\*.png submission_package\outputs 2>nul
    xcopy /Y outputs\*.csv submission_package\outputs 2>nul
    xcopy /Y outputs\*.txt submission_package\outputs 2>nul
    echo - Output samples copied
)

REM Copy documentation
copy README.md submission_package\
copy QUICKSTART.md submission_package\
copy PROJECT_SUMMARY.md submission_package\
copy requirements.txt submission_package\
copy environment.yml submission_package\
copy Dockerfile submission_package\
echo - Documentation copied

REM Copy configuration files
copy .gitignore submission_package\
echo - Configuration copied

echo.
echo =========================================
echo Package created in: submission_package\
echo =========================================
echo.
echo Next steps:
echo 1. Review the submission_package folder
echo 2. Add your presentation slides to submission_package\slides\
echo 3. Right-click submission_package folder
echo 4. Select "Send to" - "Compressed (zipped) folder"
echo 5. Rename to: vehicle-compliance-monitor-submission.zip
echo 6. Submit the ZIP file
echo.
echo Note: Videos are NOT included (too large)
echo       Mention in presentation that videos can be provided separately
echo.

pause
