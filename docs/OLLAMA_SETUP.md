# Ollama Validation Setup Guide

## ✅ What You've Installed
- **Ollama** version 0.13.2 (Windows service)
- **LLaVA** vision model (4.7GB)
- **Python requests** library

## 🚀 How to Use Ollama Validation

### Step 1: Start Ollama Service
Ollama should start automatically, but if it's not running, open PowerShell and run:

```powershell
ollama serve
```

Leave this window open - it will show the Ollama server logs.

### Step 2: Run Your OCR Script WITH Validation

**Basic usage (without validation):**
```powershell
python ocr.py "path/to/video.mp4" --out ./results
```

**WITH Ollama validation (validates every 4 seconds):**
```powershell
python ocr.py "path/to/video.mp4" --out ./results --use-ollama
```

**Custom validation interval (every 3 seconds):**
```powershell
python ocr.py "path/to/video.mp4" --out ./results --use-ollama --validation-interval 3.0
```

### Step 3: Understanding the Output

When `--use-ollama` is enabled, you'll see:

```
[VALIDATION] Running Ollama check at 4.00s...
  ✓ OCR and Ollama agree: 345.67
```

Or if there's a correction:
```
[VALIDATION] Running Ollama check at 8.00s...
  ⚠ Correction: OCR=34567 → Ollama=345.67
```

The CSV file will have two extra columns:
- `Ollama_ROI_3`: The value Ollama detected
- `Validation_Status`: One of:
  - `MATCH` - OCR and Ollama agree
  - `CORRECTED` - Ollama fixed the OCR value
  - `FILLED` - OCR missed it, Ollama found it
  - `FAILED` - Ollama couldn't read it

## 🎯 How It Works

1. **Fast Lane**: PaddleOCR runs on every frame (20 FPS) - very fast
2. **Smart Lane**: Every 3-4 seconds, Ollama double-checks the value
3. **Auto-Correction**: If Ollama disagrees with OCR, it overwrites the value

This gives you:
- ✅ Real-time speed (from PaddleOCR)
- ✅ High accuracy (from Ollama AI)
- ✅ No API costs (runs locally)
- ✅ Unlimited usage

## 🔧 Troubleshooting

### "Could not connect to Ollama"
**Solution**: Start the Ollama service:
```powershell
ollama serve
```

### Ollama is slow
**Solution**: Increase the validation interval:
```powershell
python ocr.py video.mp4 --use-ollama --validation-interval 10.0
```

### Want to test Ollama directly?
```powershell
ollama run llava
```
Then you can chat with it or send it images.

## 📊 Performance Tips

- **For fast processing**: Use `--validation-interval 10.0` (validate every 10 seconds)
- **For maximum accuracy**: Use `--validation-interval 2.0` (validate every 2 seconds)
- **For stable meters**: 4 seconds (default) is perfect

## 🎓 Example Commands

**Process a video with validation every 5 seconds:**
```powershell
python ocr.py "C:/Videos/meter.mp4" --out ./results --use-ollama --validation-interval 5.0
```

**Skip frames for speed + validation:**
```powershell
python ocr.py "C:/Videos/meter.mp4" --out ./results --frame-skip 5 --use-ollama
```

**Save annotated video + validation:**
```powershell
python ocr.py "C:/Videos/meter.mp4" --out ./results --use-ollama --save-annotated-video
```

---

## 🆚 Validation vs No Validation

| Feature | Without `--use-ollama` | With `--use-ollama` |
|---------|----------------------|-------------------|
| Speed | Very Fast (20 FPS) | Fast (20 FPS + periodic AI check) |
| Accuracy | Good | Excellent |
| Decimal Issues | May occur | Auto-corrected |
| Missing Values | May occur | Auto-filled |
| Cost | Free | Free (local) |

---

**You're all set!** 🎉

The system will now:
1. Run fast OCR on every frame
2. Validate with AI every few seconds
3. Auto-correct any mistakes
4. Save everything to CSV with validation status
