# CSV Structure Update - Headers from ROI_1 and ROI_3

## ✅ What Changed

The CSV output structure has been completely redesigned:

**OLD Structure:**
```
| frame_idx | time_sec | ROI_1 | ROI_2 | ROI_3 | ROI_4 |
|-----------|----------|-------|-------|-------|-------|
| 0         | 0.00     | Text1 | Val1  | Text2 | Val2  |
```

**NEW Structure:**
```
| frame_idx | time_sec | [ROI_1 Text] | [ROI_3 Text] | Other_Text |
|-----------|----------|--------------|--------------|------------|
| 0         | 0.00     | Val from ROI_2 | Val from ROI_4 | ...      |
```

---

## 📊 How It Works

### ROI Mapping:
- **ROI_1** → Column Header (e.g., "Total Volume")
- **ROI_2** → Data values under ROI_1 header
- **ROI_3** → Column Header (e.g., "Flow Rate")
- **ROI_4** → Data values under ROI_3 header

### Example:

If your meter shows:
- ROI_1: "Total Volume"
- ROI_2: "12345.67"
- ROI_3: "Flow Rate"
- ROI_4: "266.58"

**CSV Output:**
```
frame_idx,time_sec,Total Volume,Flow Rate,Other_Text
0,0.00,12345.67,266.58,
1,0.05,12345.68,266.59,
```

---

## 📁 Files Affected

### For Images:
- `image_results_TIMESTAMP.csv`
  - Headers: Image, [ROI_1 text], [ROI_3 text], Other_Text
  - Data: Image path, ROI_2 value, ROI_4 value, other text

### For Videos:
- `all_frames_TIMESTAMP.csv`
  - Headers determined from **first frame**
  - Headers: frame_idx, time_sec, [ROI_1 text], [ROI_3 text], Other_Text
  - Data: frame number, time, ROI_2 value, ROI_4 value, other text

- `stable_values_TIMESTAMP.csv`
  - Headers: start_time, end_time, [ROI_1 text], [ROI_3 text]
  - Data: start time, end time, ROI_2 value, ROI_4 value

---

## 🎯 Benefits

✅ **Self-documenting** - Column names come from the meter itself  
✅ **Cleaner data** - Only changing values in the CSV  
✅ **Excel-friendly** - Headers make sense when opened in Excel  
✅ **Flexible** - Works with any meter layout  

---

## 💡 Important Notes

1. **Headers are set from the FIRST FRAME** of video
   - Make sure the first frame has clear ROI_1 and ROI_3 text
   - If first frame is blurry, headers might be incorrect

2. **ROI_1 and ROI_3 should be STATIC text** (labels/headers)
   - Example: "Total Volume", "Flow Rate", "Pressure", etc.

3. **ROI_2 and ROI_4 should be CHANGING values** (the actual readings)
   - Example: "12345.67", "266.58", etc.

---

## 🚀 No Changes to Commands

All commands remain the same:

```powershell
# For images
python ocr.py "image.jpg" --mode image --out ./results

# For videos
python ocr.py "video.mp4" --out ./results

# With all features
python ocr.py "video.mp4" --out ./results --use-ollama --excel
```

The CSV structure automatically uses the new format!

---

**Your CSV files will now have meaningful column names from your meter display!** 🎉
