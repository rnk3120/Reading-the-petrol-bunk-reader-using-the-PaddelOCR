# Quick Setup Guide for Windows

## The Problem
You're experiencing a PyTorch DLL compatibility issue on Windows. This is a known problem with certain PyTorch versions.

## Solution: Use EasyOCR Instead

EasyOCR is simpler to install and works better on Windows without dependency issues.

### Step 1: Install EasyOCR
```cmd
python -m pip install easyocr opencv-python numpy pandas shapely scikit-learn
```

### Step 2: Run with EasyOCR
Since your `ocr.py` currently only supports PaddleOCR, I'll create a version that works with EasyOCR.

### Alternative: Fix PyTorch DLL Issue

If you want to stick with PaddleOCR, try these fixes:

#### Option 1: Install Visual C++ Redistributable
Download and install: https://aka.ms/vs/17/release/vc_redist.x64.exe

#### Option 2: Use older PyTorch version
```cmd
python -m pip uninstall -y torch torchvision
python -m pip install torch==2.0.1 torchvision==0.15.2
```

#### Option 3: Fresh Python Environment
Create a clean environment:
```cmd
conda create -n ocr_clean python=3.10 -y
conda activate ocr_clean
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.3
pip install opencv-python numpy pandas shapely scikit-learn
```

## Recommended: Just use the system that's already working!

Since you mentioned the script was running earlier (before we started debugging), the easiest solution is:
1. Use the Python environment where it was working
2. Or use EasyOCR which has fewer dependencies

Would you like me to create an EasyOCR version of the script?
