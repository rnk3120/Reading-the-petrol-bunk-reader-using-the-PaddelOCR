# PaddleOCR Installation for CUDA 12.2 - Quick Start Guide

## 🎯 Your Setup
- **CUDA Version**: 12.2
- **Conda Environment**: paddle_gpu
- **Required PaddlePaddle Version**: 2.6.1 (compatible with CUDA 12.0+)

---

## 🚀 Quick Installation (Copy & Paste)

Open your terminal on the Linux system and run:

```bash
# Activate your conda environment
conda activate paddle_gpu

# Install PaddlePaddle for CUDA 12.2
pip install paddlepaddle-gpu==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

# Install PaddleOCR
pip install paddleocr

# Install dependencies
pip install opencv-python numpy pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz
```

---

## ✅ Verify Installation

```bash
# Check PaddlePaddle
python3 -c "import paddle; print(f'PaddlePaddle: {paddle.__version__}'); print(f'Device: {paddle.device.get_device()}')"

# Check PaddleOCR
python3 -c "from paddleocr import PaddleOCR; print('✓ PaddleOCR is ready!')"
```

**Expected Output:**
```
PaddlePaddle: 2.6.1
Device: gpu:0
✓ PaddleOCR is ready!
```

---

## 🎬 Run Your OCR Script

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

---

## 📋 Alternative: Use the Installation Script

```bash
# Make the script executable
chmod +x install_paddle_cuda12.sh

# Run it
./install_paddle_cuda12.sh
```

---

## 🔧 Troubleshooting

### Issue: "No module named 'paddle'" after installation
**Solution:**
```bash
# Restart your terminal or re-activate the environment
conda deactivate
conda activate paddle_gpu
```

### Issue: GPU not detected
**Solution:**
```bash
# Check CUDA availability
python3 -c "import paddle; print(paddle.device.is_compiled_with_cuda())"

# Check GPU count
python3 -c "import paddle; print(paddle.device.cuda.device_count())"
```

### Issue: Installation fails
**Solution:**
```bash
# Try without the mirror
pip install paddlepaddle-gpu==2.6.1

# Or use the official source
pip install paddlepaddle-gpu==2.6.1 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

---

## 📦 What Gets Installed

| Package | Version | Purpose |
|---------|---------|---------|
| paddlepaddle-gpu | 2.6.1 | Deep learning framework (CUDA 12.2) |
| paddleocr | ≥2.7.0 | OCR engine |
| opencv-python | ≥4.5.0 | Image/video processing |
| numpy | ≥1.19.0 | Numerical operations |
| pandas | ≥1.1.0 | Data handling |
| shapely | ≥1.7.0 | Geometric operations |
| scikit-learn | ≥0.24.0 | Clustering (ROI detection) |

---

## 💡 Tips

1. **GPU Memory**: Video processing can use significant GPU memory. If you encounter OOM errors, increase `--frame-skip` value.

2. **Performance**: With CUDA 12.2 and a modern GPU, you should see significant speedup compared to CPU processing.

3. **First Run**: The first time you run PaddleOCR, it will download model files (~100MB). This is normal.

4. **Output**: Results will be saved in:
   - `./results/annotated/` - Annotated video and frames
   - `./results/per_frame/` - Per-frame OCR results (CSV)
   - `./results/grouped/` - Grouped ROI results (CSV)

---

## 📞 Need Help?

Run the diagnostic script:
```bash
python check_paddle_env.py
```

This will check all dependencies and provide specific error messages if something is missing.

---

**Last Updated**: 2025-12-03  
**CUDA Version**: 12.2  
**PaddlePaddle Version**: 2.6.1
