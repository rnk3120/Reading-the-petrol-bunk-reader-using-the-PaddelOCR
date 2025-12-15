@echo off
REM OCR with Ollama Validation - Example Script
REM Edit the VIDEO_PATH below to point to your video file

echo ========================================
echo OCR with AI Validation
echo ========================================
echo.

REM ---- CONFIGURATION ----
set VIDEO_PATH=C:\path\to\your\video.mp4
set OUTPUT_DIR=.\results
set VALIDATION_INTERVAL=4.0

REM Check if video path is set
if "%VIDEO_PATH%"=="C:\path\to\your\video.mp4" (
    echo ERROR: Please edit this script and set VIDEO_PATH to your actual video file
    echo.
    echo Example: set VIDEO_PATH=C:\Videos\meter_recording.mp4
    echo.
    pause
    exit /b 1
)

REM Check if video file exists
if not exist "%VIDEO_PATH%" (
    echo ERROR: Video file not found: %VIDEO_PATH%
    echo.
    pause
    exit /b 1
)

echo Video: %VIDEO_PATH%
echo Output: %OUTPUT_DIR%
echo Validation Interval: %VALIDATION_INTERVAL% seconds
echo.
echo Starting OCR processing with Ollama validation...
echo.

python src\ocr.py "%VIDEO_PATH%" --out "%OUTPUT_DIR%" --use-ollama --validation-interval %VALIDATION_INTERVAL%

echo.
echo ========================================
echo Processing Complete!
echo ========================================
echo.
echo Check the results folder for:
echo - all_frames_*.csv (every frame with validation status)
echo - stable_values_*.csv (only stable readings)
echo.
pause
