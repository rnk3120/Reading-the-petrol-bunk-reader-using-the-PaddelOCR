#!/bin/bash
# Complete fix for NumPy ABI compatibility issue
# This will reinstall all packages with compatible NumPy version

echo "=========================================="
echo "Complete NumPy Compatibility Fix"
echo "=========================================="
echo ""

# Check if conda environment is activated
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "⚠ ERROR: No conda environment is activated!"
    echo "Please run: conda activate paddle_gpu"
    exit 1
fi

echo "✓ Conda environment: $CONDA_DEFAULT_ENV"
echo ""

echo "Step 1: Uninstalling NumPy 2.x and affected packages..."
pip uninstall -y numpy opencv-python opencv-contrib-python

echo ""
echo "Step 2: Installing NumPy 1.23.5 (compatible version)..."
pip install "numpy==1.23.5"

echo ""
echo "Step 3: Reinstalling OpenCV with compatible NumPy..."
pip install opencv-python

echo ""
echo "Step 4: Reinstalling PaddlePaddle and PaddleOCR..."
pip install --force-reinstall --no-cache-dir paddlepaddle-gpu==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install --force-reinstall --no-cache-dir paddleocr==2.7.3

echo ""
echo "Step 5: Installing other dependencies..."
pip install pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="

python3 << 'EOF'
import sys

print("Checking installations...\n")

# Check NumPy
try:
    import numpy as np
    print(f"✓ NumPy: {np.__version__}")
    if np.__version__.startswith('2.'):
        print("  ⚠ WARNING: NumPy 2.x detected, should be 1.x")
        sys.exit(1)
except Exception as e:
    print(f"✗ NumPy error: {e}")
    sys.exit(1)

# Check OpenCV
try:
    import cv2
    print(f"✓ OpenCV: {cv2.__version__}")
except Exception as e:
    print(f"✗ OpenCV error: {e}")
    sys.exit(1)

# Check PaddlePaddle
try:
    import paddle
    print(f"✓ PaddlePaddle: {paddle.__version__}")
    print(f"  Device: {paddle.device.get_device()}")
    if paddle.device.is_compiled_with_cuda():
        print(f"  CUDA: Available (GPU count: {paddle.device.cuda.device_count()})")
except Exception as e:
    print(f"✗ PaddlePaddle error: {e}")
    sys.exit(1)

# Check PaddleOCR
try:
    from paddleocr import PaddleOCR
    print(f"✓ PaddleOCR: Imported successfully")
except Exception as e:
    print(f"✗ PaddleOCR error: {e}")
    sys.exit(1)

# Check other dependencies
try:
    import pandas
    import shapely
    from sklearn.cluster import KMeans
    print(f"✓ Pandas: {pandas.__version__}")
    print(f"✓ Shapely: {shapely.__version__}")
    print(f"✓ Scikit-learn: Imported successfully")
except Exception as e:
    print(f"⚠ Some dependencies missing: {e}")

print("\n" + "="*50)
print("Testing PaddleOCR initialization...")
print("="*50)

try:
    ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False)
    print("✓ PaddleOCR initialized successfully!")
except Exception as e:
    print(f"✗ PaddleOCR initialization failed: {e}")
    sys.exit(1)

print("\n✓ All checks passed!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Fix Complete!"
    echo "=========================================="
    echo ""
    echo "Your environment is now ready. Run your OCR script:"
    echo ""
    echo "python ocr.py /home/blp/Nitesh/OCR/OCR_Videos/petrol_reader_1.mp4 \\"
    echo "  --out ./results \\"
    echo "  --mode video \\"
    echo "  --engine paddle \\"
    echo "  --langs en \\"
    echo "  --n-rois 4 \\"
    echo "  --frame-skip 0 \\"
    echo "  --save-annotated-video"
else
    echo ""
    echo "⚠ Verification failed. Please check the errors above."
    exit 1
fi
