#!/bin/bash
# Fixed Installation for CUDA 12.2 with Compatible Versions

echo "=========================================="
echo "PaddleOCR Installation Fix for CUDA 12.2"
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

echo "Uninstalling existing PaddlePaddle and PaddleOCR..."
pip uninstall -y paddlepaddle-gpu paddlepaddle paddleocr

echo ""
echo "Installing compatible versions for CUDA 12.2..."
echo ""

# Option 1: Use PaddlePaddle 2.5.2 (more stable with PaddleOCR)
echo "Installing PaddlePaddle 2.5.2 (CUDA 12.0 compatible)..."
pip install paddlepaddle-gpu==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

if [ $? -ne 0 ]; then
    echo "⚠ Trying alternative installation method..."
    pip install paddlepaddle-gpu==2.5.2
fi

echo ""
echo "Installing PaddleOCR 2.7.3 (tested with PaddlePaddle 2.5.x)..."
pip install paddleocr==2.7.3

echo ""
echo "Installing dependencies..."
pip install opencv-python numpy pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz

echo ""
echo "=========================================="
echo "Verifying Installation..."
echo "=========================================="

python3 << 'EOF'
import sys

print("Python version:", sys.version)
print()

try:
    import paddle
    print(f"✓ PaddlePaddle version: {paddle.__version__}")
    print(f"✓ Device: {paddle.device.get_device()}")
    
    if paddle.device.is_compiled_with_cuda():
        print(f"✓ CUDA support: Available")
        print(f"✓ GPU count: {paddle.device.cuda.device_count()}")
    else:
        print("⚠ CUDA support: Not available (running on CPU)")
except Exception as e:
    print(f"✗ PaddlePaddle error: {e}")
    sys.exit(1)

print()

try:
    from paddleocr import PaddleOCR
    print("✓ PaddleOCR imported successfully")
    
    # Test initialization
    print("Testing PaddleOCR initialization...")
    ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False)
    print("✓ PaddleOCR initialized successfully")
except Exception as e:
    print(f"✗ PaddleOCR error: {e}")
    sys.exit(1)

print()
print("✓ All checks passed!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Installation Complete!"
    echo "=========================================="
    echo ""
    echo "Installed versions:"
    echo "  - PaddlePaddle: 2.5.2 (CUDA 12.0+ compatible)"
    echo "  - PaddleOCR: 2.7.3"
    echo ""
    echo "You can now run your OCR script:"
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
    echo "⚠ Installation verification failed. Please check the errors above."
    exit 1
fi
