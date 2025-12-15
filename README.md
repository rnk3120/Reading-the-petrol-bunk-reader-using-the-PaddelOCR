# ⛽ Intelligent Petrol Pump Reader (OCR + AI Validation)

![Project Banner](https://img.shields.io/badge/AI-PaddleOCR%20%2B%20Ollama-blue) ![Python](https://img.shields.io/badge/Python-3.10-yellow) ![License](https://img.shields.io/badge/License-MIT-green)

An advanced computer vision system designed to automatically read and digitize petrol pump meter displays. It combines the speed of **PaddleOCR** with the intelligence of **Local LLMs (Ollama)** to ensure high-accuracy data extraction.

---

## 📸 Output Demonstration

### 1. Annotated Visualization
The system identifies Regions of Interest (ROIs), draws bounding boxes, and overlays the detected values in real-time.

*(Upload a screenshot of your `annotated_*.jpg` here and replace the link below)*
![Annotated Output Example](docs/images/example_output.jpg)

### 2. Structured CSV Output
Instead of raw text, the system structures data into columns based on the meter's labels (e.g., "Volume", "Price").

| frame_idx | time_sec | Total Volume | Flow Rate | Validation_Status |
| :--- | :--- | :--- | :--- | :--- |
| 10 | 0.50 | 266.58 | 123.45 | MATCH ✅ |
| 11 | 0.55 | 266.58 | 123.45 | MATCH ✅ |
| ... | ... | ... | ... | ... |

---

## 🌟 Key Features

*   **⚡ Hybrid Engine:** Uses **PaddleOCR** for real-time speed (>20 FPS) and **Ollama (LLaVA)** for periodic AI verification.
*   **🧠 2-Step Confirmation Logic:** Eliminates flickering digits by waiting for values to stabilize across consecutive frames before saving.
*   **📐 Intelligent ROI Scaling:** Hardcoded regions automatically resize to fit any video resolution (720p, 1080p, 4K).
*   **📊 Self-Documenting Data:** Dynamically detects column headers from the video itself (e.g., uses "Volume" text on screen as the CSV header).
*   **🔄 Zero-Reset Handling:** Automatically handles meter resets (when values go to 0.00) without polluting the dataset.

---

## 📂 Project Structure

*   **`src/`**: Contains the core Python source code.
*   **`docs/`**: Detailed documentation and guides.
    *   [📖 **Full Project Documentation**](docs/PROJECT_DOCUMENTATION.md) (Installation, Usage, Logic)
    *   [🧠 **Confirmation Logic Guide**](docs/CONFIRMATION_LOGIC_GUIDE.md) (How the stabilization works)
    *   [📐 **Static ROI Guide**](docs/STATIC_ROI_GUIDE.md) (How to configure regions)
*   **`results/`**: Output folder for CSVs, Excel files, and annotated videos.

---

## 🚀 Quick Start

### 1. Installation
```powershell
pip install -r requirements.txt
# (See docs/PROJECT_DOCUMENTATION.md for full setup)
```

### 2. Run on Video
```powershell
python src/ocr.py "path/to/video.mp4" --out ./results
```

### 3. Run with AI Validation
```powershell
python src/ocr.py "path/to/video.mp4" --use-ollama --out ./results
```

---

## ⚙️ How It Works

1.  **Scaling:** The system reads the video resolution and scales the "Hardcoded ROIs" to match the screen perfectly.
2.  **Detection:** PaddleOCR extracts text from the regions.
3.  **Stabilization:** The logic waits for 2 consecutive frames with the same number to confirm it's not a glitch.
4.  **Validation:** Every 2 seconds, the image is sent to a local LLM (LLaVA) to cross-check the reading.
5.  **Export:** Data is saved to CSV and optionally Excel.

---

## 📝 License
This project is open-source. Feel free to use and modify it!
