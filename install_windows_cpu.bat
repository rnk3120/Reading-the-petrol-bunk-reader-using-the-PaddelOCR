@echo off
REM Windows CPU Installation Script for OCR
REM Double-click this file to run, or execute in Command Prompt

echo ==========================================
echo Windows CPU OCR Installation
echo ==========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda not found. Please install Anaconda or Miniconda first.
    echo Download from: https://www.anaconda.com/download
    pause
    exit /b 1
)

echo Step 1: Creating conda environment 'ocr_cpu'...
call conda create -n ocr_cpu python=3.10 -y

echo.
echo Step 2: Activating environment...
call conda activate ocr_cpu

echo.
echo Step 3: Installing NumPy 1.23.5...
pip install "numpy==1.23.5"

echo.
echo Step 4: Installing OpenCV...
pip install opencv-python==4.8.1.78

echo.
echo Step 5: Installing PaddlePaddle CPU version...
pip install paddlepaddle==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo Step 6: Installing PaddleOCR...
pip install paddleocr==2.7.3

echo.
echo Step 7: Installing other dependencies...
pip install pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz

echo.
echo ==========================================
echo Verifying Installation...
echo ==========================================
echo.

python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import paddle; print('PaddlePaddle:', paddle.__version__)"
python -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False); print('PaddleOCR: OK')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Installation Complete!
    echo ==========================================
    echo.
    echo To use the OCR script:
    echo 1. Activate environment: conda activate ocr_cpu
    echo 2. Run: python ocr.py "path\to\video.mp4" --out ./results --mode video --engine paddle --langs en --n-rois 4 --frame-skip 5 --save-annotated-video
    echo.
    echo Note: CPU processing is slower. Use --frame-skip 5 or higher for faster processing.
) else (
    echo.
    echo ==========================================
    echo Installation Failed
    echo ==========================================
    echo Please check the errors above.
)

echo.
pause
