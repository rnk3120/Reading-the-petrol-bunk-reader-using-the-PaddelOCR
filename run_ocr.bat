@echo off
REM Quick OCR Runner for Windows
REM Edit the VIDEO_PATH variable below to point to your video file

echo ==========================================
echo OCR Video Processor - Windows CPU
echo ==========================================
echo.

REM ========================================
REM CONFIGURATION - Edit these variables
REM ========================================

REM Path to your video file (change this!)
set VIDEO_PATH=C:\path\to\your\video.mp4

REM Output directory
set OUTPUT_DIR=.\results

REM Frame skip (higher = faster, lower = more accurate)
REM 0 = process every frame (slow)
REM 5 = process every 6th frame (recommended for CPU)
REM 10 = process every 11th frame (fast)
set FRAME_SKIP=5

REM Number of ROIs (regions of interest)
set N_ROIS=4

REM OCR Engine (paddle or easyocr)
set ENGINE=paddle

REM Language
set LANG=en

REM ========================================
REM Activate environment
REM ========================================

echo Activating conda environment 'ocr_cpu'...
call conda activate ocr_cpu

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not activate 'ocr_cpu' environment.
    echo Please run 'install_windows_cpu.bat' first to set up the environment.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Configuration:
echo ==========================================
echo Video: %VIDEO_PATH%
echo Output: %OUTPUT_DIR%
echo Frame Skip: %FRAME_SKIP%
echo ROIs: %N_ROIS%
echo Engine: %ENGINE%
echo Language: %LANG%
echo ==========================================
echo.

REM Check if video file exists
if not exist "%VIDEO_PATH%" (
    echo.
    echo ERROR: Video file not found: %VIDEO_PATH%
    echo.
    echo Please edit this batch file and set VIDEO_PATH to your video file.
    echo Right-click this file and select 'Edit' to change the path.
    pause
    exit /b 1
)

echo Starting OCR processing...
echo This may take a while on CPU. Please be patient.
echo.

REM Run OCR
python ocr.py "%VIDEO_PATH%" ^
  --out %OUTPUT_DIR% ^
  --mode video ^
  --engine %ENGINE% ^
  --langs %LANG% ^
  --n-rois %N_ROIS% ^
  --frame-skip %FRAME_SKIP% ^
  --save-annotated-video

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Processing Complete!
    echo ==========================================
    echo.
    echo Results saved to: %OUTPUT_DIR%
    echo.
    echo Contents:
    echo - Annotated video: %OUTPUT_DIR%\annotated\
    echo - Per-frame CSV: %OUTPUT_DIR%\per_frame\
    echo - Grouped CSV: %OUTPUT_DIR%\grouped\
    echo.
) else (
    echo.
    echo ==========================================
    echo Processing Failed
    echo ==========================================
    echo Please check the errors above.
)

echo.
pause
