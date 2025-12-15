#!/bin/bash
# Quick Installation for CUDA 12.2
# Run this script in your paddle_gpu conda environment

echo "=========================================="
echo "PaddleOCR Installation for CUDA 12.2"
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

# Verify CUDA version
if command -v nvidia-smi &> /dev/null; then
    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    echo "✓ Detected CUDA Version: $CUDA_VERSION"
else
    echo "⚠ WARNING: nvidia-smi not found. Cannot verify CUDA version."
fi

echo ""
echo "Installing PaddlePaddle 2.6.1 (CUDA 12.2 compatible)..."
pip install paddlepaddle-gpu==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

if [ $? -ne 0 ]; then
    echo "⚠ Installation failed. Trying alternative source..."
    pip install paddlepaddle-gpu==2.6.1
fi

echo ""
echo "Installing PaddleOCR..."
pip install paddleocr

echo ""
echo "Installing additional dependencies..."
pip install opencv-python numpy pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz

echo ""
echo "=========================================="
echo "Verifying Installation..."
echo "=========================================="

python3 << EOF
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

try:
    from paddleocr import PaddleOCR
    print("✓ PaddleOCR imported successfully")
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
