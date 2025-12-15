# Static ROI Configuration Guide

## ✅ What Changed

Your OCR script now supports **static ROI coordinates** for consistent text extraction!

---

## 📁 Files Created

1. **`roi_config.json`** - Contains your static ROI coordinates
2. **Updated `ocr.py`** - Now accepts `--roi-config` parameter

---

## 🎯 How to Use Static ROIs

### For Images:
```powershell
conda activate ocr_env
cd C:\Users\niteshk\Desktop\vs\OCR

python ocr.py "C:\Users\niteshk\Desktop\OCR\reader.jpg" --mode image --out ./results --roi-config roi_config.json
```

### For Videos:
```powershell
python ocr.py "C:\Users\niteshk\Desktop\OCR_Videos\pump_reader.mp4" --out ./results --roi-config roi_config.json
```

### With Ollama Validation:
```powershell
python ocr.py "video.mp4" --out ./results --roi-config roi_config.json --use-ollama
```

### With Excel Export:
```powershell
python ocr.py "video.mp4" --out ./results --roi-config roi_config.json --excel
```

---

## 📊 Your ROI Configuration

The `roi_config.json` file contains your 4 static regions:

```
ROI_1: Top region    (1276,700) → (2556,916)
ROI_2: Middle region (1272,941) → (2553,1248)
ROI_3: Main value    (1460,1424) → (2355,1618)  ← Usually the main reading
ROI_4: Bottom region (1265,1648) → (2573,1952)
```

---

## 🔧 How It Works

### Without `--roi-config` (Auto-detection):
- ❌ ROIs change between runs
- ❌ May group text incorrectly
- ✅ Works for any image/video

### With `--roi-config` (Static ROIs):
- ✅ Same ROIs every time
- ✅ Consistent grouping
- ✅ More accurate results
- ⚠️ Only works for images/videos with same resolution

---

## 📝 Editing ROI Coordinates

To change the ROI coordinates, edit `roi_config.json`:

```json
{
  "rois": {
    "ROI_1": [
      [x1, y1],  // Top-left
      [x2, y2],  // Top-right
      [x3, y3],  // Bottom-right
      [x4, y4]   // Bottom-left
    ]
  }
}
```

**Tip:** Use the annotated image to see where the current ROIs are, then adjust coordinates as needed.

---

## 🎨 Visual Verification

The annotated image will show:
- **Colored boxes** around each ROI region
- **ROI labels** (ROI_1, ROI_2, etc.)
- **Detected text** with confidence scores

This helps you verify that your static ROIs are correctly positioned!

---

## ⚡ Quick Commands Reference

```powershell
# Basic with static ROIs
python ocr.py "image.jpg" --mode image --roi-config roi_config.json

# Video with static ROIs
python ocr.py "video.mp4" --roi-config roi_config.json

# Full featured (static ROIs + validation + Excel)
python ocr.py "video.mp4" --roi-config roi_config.json --use-ollama --excel

# Without static ROIs (auto-detect)
python ocr.py "video.mp4"
```

---

## 💡 Best Practices

1. **Use static ROIs** when processing multiple images/videos from the same camera/setup
2. **Use auto-detection** when processing images from different sources
3. **Check the annotated image** first to verify ROI positions
4. **Adjust coordinates** in `roi_config.json` if needed

---

## 🎉 Benefits of Static ROIs

✅ **Consistency** - Same regions every time  
✅ **Accuracy** - No clustering errors  
✅ **Speed** - Slightly faster (no KMeans calculation)  
✅ **Reliability** - Works even when text is missing from some regions  

---

**You're all set!** Your static ROIs are configured and ready to use. 🚀
