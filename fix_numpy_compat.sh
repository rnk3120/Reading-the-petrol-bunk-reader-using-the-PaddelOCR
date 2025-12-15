#!/bin/bash
# Fix NumPy compatibility issue with PaddlePaddle 2.5.2

echo "=========================================="
echo "Fixing NumPy Compatibility"
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

# Check current NumPy version
echo "Current NumPy version:"
python3 -c "import numpy; print(numpy.__version__)"
echo ""

# Downgrade NumPy to compatible version
echo "Installing NumPy 1.23.5 (compatible with PaddlePaddle 2.5.2)..."
pip install "numpy<2.0.0" --force-reinstall

echo ""
echo "New NumPy version:"
python3 -c "import numpy; print(numpy.__version__)"

echo ""
echo "=========================================="
echo "Testing PaddlePaddle..."
echo "=========================================="

python3 << 'EOF'
import paddle
import numpy as np

print(f"✓ PaddlePaddle: {paddle.__version__}")
print(f"✓ NumPy: {np.__version__}")
print(f"✓ Device: {paddle.device.get_device()}")

if paddle.device.is_compiled_with_cuda():
    print(f"✓ CUDA: Available")
    print(f"✓ GPU count: {paddle.device.cuda.device_count()}")
else:
    print("⚠ CUDA: Not available")
EOF

echo ""
echo "=========================================="
echo "Testing PaddleOCR..."
echo "=========================================="

python3 << 'EOF'
from paddleocr import PaddleOCR

print("Initializing PaddleOCR...")
ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False)
print("✓ PaddleOCR initialized successfully!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ All Fixed!"
    echo "=========================================="
    echo ""
    echo "You can now run your OCR script:"
    echo "python ocr.py /home/blp/Nitesh/OCR/OCR_Videos/petrol_reader_1.mp4 --out ./results --mode video --engine paddle --langs en --n-rois 4 --frame-skip 0 --save-annotated-video"
else
    echo ""
    echo "⚠ There were errors. Please check the output above."
    exit 1
fi
