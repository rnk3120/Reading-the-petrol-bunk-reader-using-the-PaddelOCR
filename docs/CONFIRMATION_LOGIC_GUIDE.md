# Confirmation Logic - Save Only Stable Values

## ✅ New Behavior

The script now uses **confirmation logic** to save only stable, verified values.

---

## 🎯 How It Works

### 1. **First Occurrence** - Track Only
When a new value appears, it's tracked but NOT saved yet.
```
Frame 10: ROI_2=266.58 → [TRACKING] Waiting for confirmation...
```

### 2. **Second Occurrence** - Confirm & Save
If the SAME value appears again, it's confirmed stable and SAVED.
```
Frame 11: ROI_2=266.58 → [CONFIRMED] Values stable → SAVING to CSV
```

### 3. **Third+ Occurrence** - Skip
Already saved, no need to save again.
```
Frame 12: ROI_2=266.58 → (skipped, already saved)
Frame 13: ROI_2=266.58 → (skipped, already saved)
```

### 4. **Value Changes** - Reset & Track
When value changes, start tracking the new value.
```
Frame 14: ROI_2=266.60 → [TRACKING] New value, waiting...
Frame 15: ROI_2=266.60 → [CONFIRMED] Stable → SAVING
```

### 5. **Zero Values** - Reset Everything
When values become 0 or 0.00, reset tracking (but don't save zeros).
```
Frame 20: ROI_2=0.00 → Reset tracker, don't save
Frame 21: ROI_2=100.00 → [TRACKING] New cycle started
Frame 22: ROI_2=100.00 → [CONFIRMED] Stable → SAVING
```

---

## 📊 Example Video Processing

**Input frames:**
```
Frame 1:  ROI_2=266.58, ROI_4=123.45  → Track
Frame 2:  ROI_2=266.58, ROI_4=123.45  → SAVE (confirmed)
Frame 3:  ROI_2=266.58, ROI_4=123.45  → Skip
Frame 4:  ROI_2=266.58, ROI_4=123.45  → Skip
Frame 5:  ROI_2=266.60, ROI_4=123.50  → Track (new value)
Frame 6:  ROI_2=266.60, ROI_4=123.50  → SAVE (confirmed)
Frame 7:  ROI_2=266.60, ROI_4=123.50  → Skip
Frame 8:  ROI_2=0.00, ROI_4=0.00      → Reset (don't save)
Frame 9:  ROI_2=100.00, ROI_4=50.00   → Track
Frame 10: ROI_2=100.00, ROI_4=50.00   → SAVE (confirmed)
```

**CSV Output:**
```csv
frame_idx,time_sec,Total Volume,Flow Rate
2,0.10,266.58,123.45
6,0.30,266.60,123.50
10,0.50,100.00,50.00
```

---

## 💡 Benefits

✅ **No duplicates** - Each unique value saved only once  
✅ **Confirmed stable** - Only saves values that appear twice (reduces OCR errors)  
✅ **No zeros** - Skips 0.00 values (usually means meter reset)  
✅ **Auto-reset** - Starts fresh after zero values  
✅ **Smaller CSV** - Only meaningful data points  

---

## 🚀 Console Output

You'll see messages like:
```
[TRACKING] New values: 266.58, 123.45 (waiting for confirmation)
[CONFIRMED] Values stable: 266.58, 123.45 → SAVING
[TRACKING] New values: 266.60, 123.50 (waiting for confirmation)
[CONFIRMED] Values stable: 266.60, 123.50 → SAVING
```

---

## 📝 Command (No Changes)

```powershell
conda activate ocr_env
cd C:\Users\niteshk\Desktop\vs\OCR
python ocr.py "C:\Users\niteshk\Desktop\OCR_Videos\pump_reader.mp4" --out ./results
```

The confirmation logic is **always active** - no flags needed!

---

**Your CSV will now contain only confirmed, stable values!** 🎉
