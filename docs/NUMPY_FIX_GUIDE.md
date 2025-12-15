# 🔴 CRITICAL: NumPy 2.x Compatibility Issue - COMPLETE FIX

## ❌ Current Problem

```
RuntimeError: module compiled against ABI version 0x1000009 but this version of numpy is 0x2000000
ERROR: opencv-python (cv2) is required: numpy.core.multiarray failed to import
```

**Root Cause**: NumPy 2.x has breaking ABI changes that are incompatible with:
- PaddlePaddle 2.5.2
- OpenCV (compiled against NumPy 1.x)

---

## ✅ Complete Solution

You need to **downgrade NumPy to 1.23.5** and **reinstall** all packages that depend on it.

---

## 🚀 Quick Fix (Copy & Paste)

Run these commands on your Linux system:

```bash
# 1. Remove incompatible packages
pip uninstall -y numpy opencv-python opencv-contrib-python

# 2. Install NumPy 1.23.5
pip install "numpy==1.23.5"

# 3. Reinstall OpenCV
pip install opencv-python

# 4. Reinstall PaddlePaddle (force reinstall to link with NumPy 1.x)
pip install --force-reinstall --no-cache-dir paddlepaddle-gpu==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. Reinstall PaddleOCR
pip install --force-reinstall --no-cache-dir paddleocr==2.7.3

# 6. Verify (should show NO warnings)
python3 -c "import numpy; print('NumPy:', numpy.__version__)"
python3 -c "import cv2; print('OpenCV works!')"
python3 -c "import paddle; print('PaddlePaddle works!')"
```

---

## 📋 Alternative: Use Automated Script

```bash
chmod +x complete_fix.sh
./complete_fix.sh
```

This script will:
1. ✅ Uninstall NumPy 2.x and affected packages
2. ✅ Install NumPy 1.23.5
3. ✅ Reinstall all dependencies with correct NumPy
4. ✅ Verify all installations
5. ✅ Test PaddleOCR initialization

---

## 🔍 Why This Happens

| Package | Compiled Against | Your Version | Compatible? |
|---------|------------------|--------------|-------------|
| PaddlePaddle 2.5.2 | NumPy 1.x (ABI 0x1000009) | NumPy 2.x (ABI 0x2000000) | ❌ No |
| OpenCV | NumPy 1.x | NumPy 2.x | ❌ No |
| **After Fix** | | | |
| PaddlePaddle 2.5.2 | NumPy 1.x | NumPy 1.23.5 | ✅ Yes |
| OpenCV | NumPy 1.x | NumPy 1.23.5 | ✅ Yes |

---

## ✅ Expected Versions After Fix

```bash
numpy                    1.23.5
opencv-python            4.10.0.84 (or similar)
paddleocr                2.7.3
paddlepaddle-gpu         2.5.2
```

---

## 🧪 Verification Steps

After running the fix, verify with these commands:

```bash
# 1. Check NumPy version (should be 1.23.5)
python3 -c "import numpy; print('NumPy:', numpy.__version__)"

# 2. Test OpenCV (should work without warnings)
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"

# 3. Test PaddlePaddle (should work without warnings)
python3 -c "import paddle; print('PaddlePaddle:', paddle.__version__)"

# 4. Test PaddleOCR initialization
python3 << 'EOF'
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='en', use_angle_cls=True, show_log=False)
print('✓ PaddleOCR initialized successfully!')
EOF
```

**Expected Output**: No warnings, all imports successful.

---

## 🎬 After Fix - Run Your OCR Script

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

## 🔧 Troubleshooting

### If you still see NumPy warnings:

```bash
# Check which NumPy is installed
pip list | grep numpy

# If it shows 2.x, force uninstall and reinstall
pip uninstall -y numpy
pip install "numpy==1.23.5"

# Then reinstall PaddlePaddle
pip install --force-reinstall --no-cache-dir paddlepaddle-gpu==2.5.2
```

### If OpenCV still fails:

```bash
# Reinstall OpenCV
pip uninstall -y opencv-python opencv-contrib-python
pip install opencv-python
```

### If PaddleOCR fails to initialize:

```bash
# Clear cache and reinstall
rm -rf ~/.paddleocr
rm -rf ~/.paddlex
pip install --force-reinstall --no-cache-dir paddleocr==2.7.3
```

---

## 📊 Summary

| Issue | Solution | Status |
|-------|----------|--------|
| NumPy 2.x incompatible | Downgrade to 1.23.5 | ⚠️ **Action Required** |
| OpenCV fails to import | Reinstall after NumPy fix | ⚠️ **Action Required** |
| PaddlePaddle ABI error | Force reinstall after NumPy fix | ⚠️ **Action Required** |

---

## 💡 Important Notes

1. **Order Matters**: Install NumPy first, then other packages
2. **Force Reinstall**: Use `--force-reinstall --no-cache-dir` for PaddlePaddle
3. **NumPy 1.23.5**: This is the last stable 1.x version before 2.0
4. **CUDA Compatibility**: NumPy version doesn't affect CUDA support

---

## 📁 Files Available

| File | Purpose |
|------|---------|
| **`CRITICAL_FIX.txt`** | This guide |
| **`complete_fix.sh`** | Automated fix script |
| **`fix_numpy_compat.sh`** | NumPy-only fix script |

---

**Action Required**: Run the fix commands above to resolve the NumPy compatibility issue.

**Last Updated**: 2025-12-03  
**NumPy Required**: 1.23.5 (not 2.x)  
**Status**: 🔴 Critical - Must fix before running OCR
