#!/bin/bash
# Installation script for PaddleOCR on Linux

echo "=========================================="
echo "PaddleOCR Installation Script"
echo "=========================================="
echo ""

# Check if conda environment is activated
if [[ -z "$CONDA_DEFAULT_ENV" ]]; then
    echo "⚠ No conda environment is activated!"
    echo "Please run: conda activate paddle_gpu"
    exit 1
fi

echo "Current conda environment: $CONDA_DEFAULT_ENV"
echo ""

# Detect CUDA version
if command -v nvidia-smi &> /dev/null; then
    echo "Detecting CUDA version..."
    CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
    echo "CUDA Version: $CUDA_VERSION"
    echo ""
else
    echo "⚠ nvidia-smi not found. Installing CPU version."
    CUDA_VERSION=""
fi

# Install PaddlePaddle
echo "Installing PaddlePaddle..."
if [[ ! -z "$CUDA_VERSION" ]]; then
    # GPU version
    if [[ "$CUDA_VERSION" == "11.2"* ]]; then
        pip install paddlepaddle-gpu==2.5.1
    elif [[ "$CUDA_VERSION" == "11.6"* ]]; then
        pip install paddlepaddle-gpu==2.5.1.post116 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
    elif [[ "$CUDA_VERSION" == "11.7"* ]]; then
        pip install paddlepaddle-gpu==2.5.1.post117 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
    elif [[ "$CUDA_VERSION" == "12.0"* ]]; then
        pip install paddlepaddle-gpu==2.6.1.post120 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
    elif [[ "$CUDA_VERSION" == "12.2"* ]] || [[ "$CUDA_VERSION" == "12.1"* ]]; then
        echo "Installing PaddlePaddle for CUDA 12.2..."
        pip install paddlepaddle-gpu==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
    else
        echo "⚠ CUDA version $CUDA_VERSION - trying latest GPU version compatible with CUDA 12.x..."
        pip install paddlepaddle-gpu==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
    fi
else
    # CPU version
    pip install paddlepaddle==2.5.1
fi

echo ""
echo "Installing PaddleOCR and dependencies..."
pip install paddleocr opencv-python numpy pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz

echo ""
echo "=========================================="
echo "Verifying installation..."
echo "=========================================="
python -c "import paddle; print(f'PaddlePaddle version: {paddle.__version__}')"
python -c "from paddleocr import PaddleOCR; print('✓ PaddleOCR imported successfully')"

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "You can now run your OCR script:"
echo "python ocr.py /path/to/video.mp4 --out ./results --mode video --engine paddle --langs en --n-rois 4 --frame-skip 0 --save-annotated-video"
