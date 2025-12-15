# Windows CPU OCR Setup - Complete Guide

## ✅ Yes! You Can Run on Windows CPU

Your OCR script will work perfectly on Windows CPU. It will be **slower than GPU** but fully functional.

---

## 🚀 Quick Installation (Choose One Method)

### **Method 1: Automated (Easiest)**

1. **Double-click** `install_windows_cpu.bat`
2. Wait for installation to complete
3. Done!

### **Method 2: Manual Commands**

Open **PowerShell** or **Command Prompt** and run:

```cmd
conda create -n ocr_cpu python=3.10 -y
conda activate ocr_cpu
pip install "numpy==1.23.5"
pip install opencv-python==4.8.1.78
pip install paddlepaddle==2.5.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install paddleocr==2.7.3
pip install pandas shapely scikit-learn Pillow pyclipper lmdb tqdm visualdl python-Levenshtein rapidfuzz
```

---

## 🎬 Running Your OCR Script on Windows

### **For Video:**

```cmd
conda activate ocr_cpu
python ocr.py "C:\path\to\your\video.mp4" --out ./results --mode video --engine paddle --langs en --n-rois 4 --frame-skip 5 --save-annotated-video
```

### **For Image:**

```cmd
conda activate ocr_cpu
python ocr.py "C:\path\to\your\image.jpg" --out ./results --mode image --engine paddle --langs en --n-rois 4
```

---

## ⚡ Performance Tips for CPU

| Setting | GPU | CPU (Recommended) | Why |
|---------|-----|-------------------|-----|
| `--frame-skip` | 0 | 5-10 | Process every 6th-11th frame |
| Video resolution | Any | 720p or lower | Faster processing |
| `--n-rois` | 4-6 | 2-4 | Fewer ROIs = faster |

### **Example for faster CPU processing:**

```cmd
python ocr.py "video.mp4" --out ./results --mode video --engine paddle --langs en --n-rois 2 --frame-skip 10 --save-annotated-video
```

This will:
- Process every 11th frame (much faster)
- Use only 2 ROIs (simpler clustering)
- Still give you good results

---

## 📊 Expected Performance

| Hardware | Processing Speed | 1-min Video |
|----------|------------------|-------------|
| GPU (CUDA 12.2) | 20-30 FPS | ~2-3 minutes |
| CPU (Modern i7/i9) | 1-3 FPS | ~20-60 minutes |
| CPU with frame-skip 10 | 10-30 FPS | ~2-6 minutes |

**Recommendation**: Use `--frame-skip 5` or higher on CPU for practical processing times.

---

## 🔧 Key Differences: GPU vs CPU

| Feature | GPU Version | CPU Version |
|---------|-------------|-------------|
| Package | `paddlepaddle-gpu` | `paddlepaddle` |
| CUDA Required | Yes | No |
| Speed | Fast | Slower |
| Installation | Complex | Simple |
| Windows Support | Limited | ✅ Excellent |
| All Features | ✅ | ✅ |

---

## 📦 What Gets Installed (Windows CPU)

```
numpy                    1.23.5
opencv-python            4.8.1.78
paddlepaddle             2.5.2      (CPU version)
paddleocr                2.7.3
pandas                   latest
shapely                  latest
scikit-learn             latest
```

---

## ✅ Verification

After installation, verify everything works:

```cmd
conda activate ocr_cpu
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import cv2; print('OpenCV: OK')"
python -c "import paddle; print('PaddlePaddle: OK')"
python -c "from paddleocr import PaddleOCR; print('PaddleOCR: OK')"
```

**Expected output**: All imports should succeed with no errors.

---

## 🎯 Example: Process a Video

```cmd
REM Activate environment
conda activate ocr_cpu

REM Navigate to your OCR directory
cd C:\Users\niteshk\Desktop\vs

REM Process video (adjust path to your video)
python ocr.py "C:\path\to\petrol_reader_1.mp4" ^
  --out ./results ^
  --mode video ^
  --engine paddle ^
  --langs en ^
  --n-rois 4 ^
  --frame-skip 5 ^
  --save-annotated-video
```

**Note**: Use `^` for line continuation in Windows CMD, or remove line breaks.

---

## 🆚 Alternative: Use EasyOCR (Even Simpler)

If you want even simpler installation:

```cmd
conda create -n ocr_easy python=3.10 -y
conda activate ocr_easy
pip install easyocr opencv-python pandas shapely scikit-learn
```

Then run with `--engine easyocr`:

```cmd
python ocr.py "video.mp4" --out ./results --mode video --engine easyocr --langs en --n-rois 4 --frame-skip 5 --save-annotated-video
```

---

## 🔍 Troubleshooting

### Issue: "conda not found"
**Solution**: Install Anaconda from https://www.anaconda.com/download

### Issue: Installation fails
**Solution**: 
```cmd
pip install --upgrade pip
pip install --no-cache-dir paddlepaddle==2.5.2
```

### Issue: OCR is too slow
**Solution**: Increase `--frame-skip` value:
```cmd
--frame-skip 10  # Process every 11th frame
```

### Issue: Out of memory
**Solution**: Process smaller videos or reduce resolution first:
```cmd
# Use ffmpeg to reduce resolution
ffmpeg -i input.mp4 -vf scale=1280:720 output_720p.mp4
```

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| **`WINDOWS_CPU_INSTALL.txt`** | Installation commands |
| **`install_windows_cpu.bat`** | Automated installer (double-click) |
| **`WINDOWS_CPU_GUIDE.md`** | This complete guide |
| **`ocr.py`** | Your OCR script (already compatible) |

---

## 💡 Advantages of Windows CPU

✅ **No CUDA/GPU setup needed**  
✅ **Simpler installation**  
✅ **No NumPy compatibility issues**  
✅ **Works on any Windows PC**  
✅ **All features supported**  
✅ **Good for testing and development**

---

## 🎯 Recommended Workflow

1. **Install**: Run `install_windows_cpu.bat`
2. **Test**: Process a short video first (10-30 seconds)
3. **Optimize**: Adjust `--frame-skip` based on results
4. **Process**: Run on full videos with optimized settings

---

## 📞 Quick Start Summary

```cmd
# 1. Install (one time)
install_windows_cpu.bat

# 2. Activate (every time)
conda activate ocr_cpu

# 3. Run OCR
python ocr.py "your_video.mp4" --out ./results --mode video --engine paddle --langs en --n-rois 4 --frame-skip 5 --save-annotated-video
```

---

**Ready to install? Double-click `install_windows_cpu.bat` or run the manual commands!** 🚀

The installation takes about 5-10 minutes and you'll be ready to process videos on Windows CPU.
