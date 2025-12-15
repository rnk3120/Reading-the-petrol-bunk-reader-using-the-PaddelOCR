#!/bin/bash
# ULTIMATE FIX - Complete environment rebuild for NumPy compatibility
# This will completely fix the NumPy 2.x issue

echo "=========================================="
echo "ULTIMATE FIX - NumPy Compatibility"
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

echo "Current NumPy version:"
python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "NumPy import failed"
echo ""

echo "=========================================="
echo "Step 1: Uninstalling ALL affected packages"
echo "=========================================="
pip uninstall -y numpy opencv-python opencv-contrib-python paddlepaddle-gpu paddlepaddle paddleocr

echo ""
echo "=========================================="
echo "Step 2: Installing NumPy 1.23.5"
echo "=========================================="
pip install "numpy==1.23.5"

echo ""
echo "Verifying NumPy installation:"
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"

echo ""
echo "=========================================="
echo "Step 3: Installing OpenCV"
echo "=========================================="
pip install opencv-python==4.8.1.78

echo ""
echo "=========================================="
echo "Step 4: Installing PaddlePaddle 2.5.2"
echo "=========================================="
pip install paddlepaddle-gpu==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "=========================================="
echo "Step 5: Installing PaddleOCR 2.7.3"
echo "=========================================="
pip install paddleocr==2.7.3

echo ""
echo "=========================================="
echo "Step 6: Installing other dependencies"
echo "=========================================="
pip install pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz

echo ""
echo "=========================================="
echo "VERIFICATION"
echo "=========================================="

python3 << 'EOF'
import sys

print("\n" + "="*50)
print("Checking all packages...")
print("="*50 + "\n")

errors = []

# Check NumPy
try:
    import numpy as np
    print(f"✓ NumPy: {np.__version__}")
    if np.__version__.startswith('2.'):
        print("  ⚠ ERROR: NumPy is still 2.x!")
        errors.append("NumPy version is 2.x")
except Exception as e:
    print(f"✗ NumPy: {e}")
    errors.append(f"NumPy: {e}")

# Check OpenCV
try:
    import cv2
    print(f"✓ OpenCV: {cv2.__version__}")
except Exception as e:
    print(f"✗ OpenCV: {e}")
    errors.append(f"OpenCV: {e}")

# Check PaddlePaddle
try:
    import paddle
    print(f"✓ PaddlePaddle: {paddle.__version__}")
    print(f"  Device: {paddle.device.get_device()}")
    if paddle.device.is_compiled_with_cuda():
        print(f"  CUDA: Available (GPUs: {paddle.device.cuda.device_count()})")
except Exception as e:
    print(f"✗ PaddlePaddle: {e}")
    errors.append(f"PaddlePaddle: {e}")

# Check PaddleOCR
try:
    from paddleocr import PaddleOCR
    print(f"✓ PaddleOCR: Imported")
except Exception as e:
    print(f"✗ PaddleOCR: {e}")
    errors.append(f"PaddleOCR: {e}")

# Check other dependencies
try:
    import pandas
    import shapely
    from sklearn.cluster import KMeans
    print(f"✓ Other dependencies: OK")
except Exception as e:
    print(f"⚠ Some dependencies: {e}")

print("\n" + "="*50)
print("Testing PaddleOCR initialization...")
print("="*50 + "\n")

try:
    ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False)
    print("✓ PaddleOCR initialized successfully!\n")
except Exception as e:
    print(f"✗ PaddleOCR initialization failed: {e}\n")
    errors.append(f"PaddleOCR init: {e}")

if errors:
    print("="*50)
    print("⚠ ERRORS FOUND:")
    print("="*50)
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("="*50)
    print("✓ ALL CHECKS PASSED!")
    print("="*50)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ FIX COMPLETE - READY TO USE!"
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
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠ FIX FAILED - See errors above"
    echo "=========================================="
    echo ""
    echo "If NumPy is still 2.x, try:"
    echo "  conda install numpy=1.23.5 -y"
    echo "  pip install --force-reinstall opencv-python==4.8.1.78"
    echo "  pip install --force-reinstall paddlepaddle-gpu==2.5.2"
    exit 1
fi
