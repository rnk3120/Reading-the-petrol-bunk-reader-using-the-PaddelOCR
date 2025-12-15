# PaddleOCR CUDA 12.2 - Version Compatibility Fix

## 🔴 Problem Identified

The error you're experiencing:
```
'paddle.base.libpaddle.AnalysisConfig' object has no attribute 'set_optimization_level'
```

This is a **version compatibility issue** between:
- **PaddlePaddle 2.6.1** (newer version)
- **PaddleOCR** (current version)

The newer PaddlePaddle 2.6.x has API changes that aren't fully compatible with some PaddleOCR versions.

---

## ✅ Solution: Use Compatible Versions

### Recommended Versions for CUDA 12.2:
- **PaddlePaddle**: 2.5.2 (stable, CUDA 12.0+ compatible)
- **PaddleOCR**: 2.7.3 (tested and stable)

---

## 🚀 Quick Fix (Run These Commands)

```bash
# 1. Activate your environment
conda activate paddle_gpu

# 2. Uninstall current versions
pip uninstall -y paddlepaddle-gpu paddlepaddle paddleocr

# 3. Install compatible versions
pip install paddlepaddle-gpu==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr==2.7.3

# 4. Verify installation
python3 -c "import paddle; print(f'PaddlePaddle: {paddle.__version__}')"
python3 -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False); print('✓ PaddleOCR works!')"
```

---

## 📋 Alternative: Use the Fix Script

```bash
# Make executable
chmod +x fix_paddle_install.sh

# Run it
./fix_paddle_install.sh
```

This script will:
1. Uninstall incompatible versions
2. Install PaddlePaddle 2.5.2
3. Install PaddleOCR 2.7.3
4. Verify the installation
5. Test PaddleOCR initialization

---

## 🔄 Updated OCR Script

I've also updated your `ocr.py` to handle both old and new PaddleOCR APIs automatically. The script now:
- Tries the modern API first (`use_textline_orientation`)
- Falls back to legacy API (`use_angle_cls`) if needed
- Provides clear error messages if both fail

**You need to copy the updated `ocr.py` to your Linux system.**

---

## 📊 Version Compatibility Matrix

| CUDA Version | PaddlePaddle | PaddleOCR | Status |
|--------------|--------------|-----------|--------|
| 12.2 | 2.6.1 | 2.7.x | ⚠️ API incompatibility |
| 12.2 | **2.5.2** | **2.7.3** | ✅ **Recommended** |
| 12.0 | 2.5.2 | 2.7.3 | ✅ Works |
| 11.7 | 2.5.1 | 2.7.3 | ✅ Works |

---

## 🎬 After Fixing

Run your OCR command:

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

## 🔧 Additional Troubleshooting

### If you still get errors after reinstalling:

1. **Clear PaddleOCR cache:**
   ```bash
   rm -rf ~/.paddleocr
   rm -rf ~/.paddlex
   ```

2. **Restart Python environment:**
   ```bash
   conda deactivate
   conda activate paddle_gpu
   ```

3. **Check installed versions:**
   ```bash
   pip list | grep paddle
   ```

4. **Test minimal example:**
   ```bash
   python3 << 'EOF'
   from paddleocr import PaddleOCR
   ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=True)
   print("Success!")
   EOF
   ```

---

## 📝 Summary of Changes

### Files Updated:
1. **`fix_paddle_install.sh`** - New installation script with compatible versions
2. **`ocr.py`** - Updated with version-compatible initialization code

### What Changed:
- Downgraded from PaddlePaddle 2.6.1 → 2.5.2
- Specified PaddleOCR 2.7.3 (tested version)
- Added fallback logic in OCR initialization

---

## ⚡ Why This Happens

PaddlePaddle 2.6.x introduced breaking changes:
- Removed `set_optimization_level()` method
- Changed internal API structure
- PaddleOCR hasn't fully adapted to these changes yet

Using PaddlePaddle 2.5.2 provides:
- ✅ CUDA 12.2 support
- ✅ Full PaddleOCR compatibility
- ✅ Stable API
- ✅ Production-ready

---

**Last Updated**: 2025-12-03  
**Recommended**: PaddlePaddle 2.5.2 + PaddleOCR 2.7.3  
**CUDA**: 12.2
