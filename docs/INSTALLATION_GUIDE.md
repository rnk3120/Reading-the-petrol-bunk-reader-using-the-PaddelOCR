# PaddleOCR Installation Guide

## Problem
You're getting the error: `No module named 'paddle'` because PaddlePaddle is not installed in your conda environment.

## Solution Steps

### Step 1: Activate Your Conda Environment
```bash
conda activate paddle_gpu
```

### Step 2: Check Your CUDA Version (if using GPU)
```bash
nvidia-smi
```
Look for the CUDA version in the output. Common versions are 11.2, 11.6, 11.7, 12.0, etc.

### Step 3: Install PaddlePaddle

#### For GPU (CUDA 11.2):
```bash
python -m pip install paddlepaddle-gpu==2.5.1 -i https://mirror.baidu.com/pypi/simple
```

#### For GPU (CUDA 11.6):
```bash
python -m pip install paddlepaddle-gpu==2.5.1.post116 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

#### For GPU (CUDA 11.7):
```bash
python -m pip install paddlepaddle-gpu==2.5.1.post117 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

#### For GPU (CUDA 12.0):
```bash
python -m pip install paddlepaddle-gpu==2.6.1.post120 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

#### For GPU (CUDA 12.2 - YOUR VERSION):
```bash
# PaddlePaddle 2.6.1 supports CUDA 12.0+
python -m pip install paddlepaddle-gpu==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### For CPU Only:
```bash
python -m pip install paddlepaddle==2.5.1 -i https://mirror.baidu.com/pypi/simple
```

### Step 4: Install PaddleOCR
```bash
pip install paddleocr>=2.7.0
```

### Step 5: Install Other Dependencies
```bash
pip install -r requirements_paddle.txt
```

### Step 6: Verify Installation
```bash
python -c "import paddle; print(paddle.__version__)"
python -c "from paddleocr import PaddleOCR; print('PaddleOCR imported successfully')"
```

## Alternative: Quick Install All Dependencies

If you want to install everything at once:

```bash
# Activate environment
conda activate paddle_gpu

# Install PaddlePaddle GPU (adjust CUDA version as needed)
pip install paddlepaddle-gpu==2.5.1

# Install all other requirements
pip install paddleocr opencv-python numpy pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz
```

## Troubleshooting

### Issue: CUDA version mismatch
**Solution**: Install the PaddlePaddle version that matches your CUDA version. Check the [official PaddlePaddle installation guide](https://www.paddlepaddle.org.cn/install/quick).

### Issue: Import errors after installation
**Solution**: 
1. Restart your terminal
2. Reactivate the conda environment
3. Try importing again

### Issue: GPU not detected
**Solution**:
```bash
python -c "import paddle; print(paddle.device.get_device())"
```
If it shows CPU, you may need to reinstall the correct GPU version.

## Running Your OCR Script

After successful installation, run your script:

```bash
python ocr.py /home/blp/Nitesh/OCR/OCR_Videos/petrol_reader_1.mp4 \
  --out ./results \
  --mode video \
  --engine paddle \
  --langs en \
  --n-rois 4 \
  --frame-skip 0 \
  --save-annotated-video
```

## Notes

1. The deprecation warning about `use_angle_cls` has been fixed in the code (line 101 now uses `use_textline_orientation=True` and `cls=True`)
2. Make sure you have enough disk space for video processing
3. GPU processing will be significantly faster than CPU for video files
