# 📘 Intelligent Meter OCR & Validation System - Technical Documentation

## 1. Project Overview
This project is an advanced Optical Character Recognition (OCR) system designed to extract numerical readings from industrial meter displays (e.g., pump readers) in video or image formats. Unlike standard OCR tools, this system implements **intelligent ROI (Region of Interest) scaling**, **temporal data confirmation**, and **AI-powered cross-validation** using a Local Large Language Model (LLM).

The system ensures high accuracy by comparing OCR results across consecutive frames and periodically validating them with visual AI (Ollama/LLaVA) to correct potential misreadings.

---

## 2. 🛠️ Technologies Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **OCR Engine** | **PaddleOCR** (Baidu) | Primary text detection model (DB algorithm) and recognition model (SVTR). |
| **Validation AI** | **Ollama** + **LLaVA** | Local Vision-Language Model used to "double-check" readings when requested. |
| **Computer Vision** | **OpenCV** (`cv2`) | Video frame extraction, image pre-processing, and annotation drawing. |
| **Geometry Logic** | **Shapely** | Polygon operations to determine if detected text falls inside specific regions (ROI). |
| **Data Processing** | **Pandas** & **NumPy** | Data structuring, CSV generation, and Excel export. |
| **String Matching** | **Difflib** (Levenshtein) | Fuzzy matching to compare OCR results vs AI results. |

---

## 3. 📋 Prerequisites

### Software
*   **OS:** Windows 10/11 (Project tested on Windows).
*   **Python:** Version 3.10 (Recommended for PaddleOCR compatibility).
*   **Conda:** For environment management.
*   **Visual C++ Redistributable:** Required for deep learning libraries.

### Hardware
*   **CPU:** Modern Multi-core CPU (PaddleOCR is optimized for CPU).
*   **RAM:** 8GB minimum (16GB recommended if using Ollama).
*   **Storage:** ~5GB for Ollama models + Python env.

---

## 4. ⚙️ Installation Guide

### Step 1: Set up Python Environment
```powershell
condaconcreate -n ocr_env python=3.10
conda activate ocr_env
```

### Step 2: Install Dependencies
```powershell
# Core OCR and Vision libraries
pip install paddlepaddle paddleocr opencv-python opencv-contrib-python

# Data handling and Geometry
pip install pandas shapely openpyxl requests

# Standard libraries
pip install scikit-learn
```

### Step 3: Setup Ollama (Optional for Validation)
1.  Download **Ollama** from [ollama.com](https://ollama.com).
2.  Install and ensure it's running via system tray.
3.  Pull the vision model:
    ```powershell
    ollama pull llava
    ```

---

## 5. 💻 Usage Guide

### Basic Video Processing (Fastest)
Use this for standard OCR without AI validation.
```powershell
python ocr.py "path/to/video.mp4" --out ./results
```

### Video Processing with AI Validation (Most Accurate)
Adds an extra layer of checking every 2 seconds.
```powershell
python ocr.py "path/to/video.mp4" --out ./results --use-ollama
```

### Image Processing
```powershell
python ocr.py "path/to/image.jpg" --mode image --out ./results
```

### Main Flags
*   `--use-ollama`: Enable AI validation.
*   `--validation-interval N`: Check with AI every N seconds (Default: 2.0).
*   `--excel`: Save output as `.xlsx` in addition to CSV.
*   `--roi-config file.json`: Use external ROI config (overrides hardcoded).

---

## 6. 🔍 Code Logic & Function Breakdown

### `ocr.py` - The Core Engine

#### A. Initialization & Patching
*   **`apply_paddle_patch()`**: PaddlePaddle 2.6+ removed certain deprecated optimizations that PaddleOCR relies on. This function monkey-patches the library at runtime to prevent crashes.

#### B. ROI Management
*   **`get_hardcoded_rois(target_w, target_h)`**: 
    *   **Logic:** Stores the master coordinates based on a 6000x3610 reference resolution.
    *   **Scaling:** Accepts the actual video dimensions (e.g., 1280x720) and calculates scale factors (`scale_x`, `scale_y`). It multiplies all polygon points by these factors so ROIs fit perfectly on any resolution.

#### C. Pre-processing & Detection
*   **`OCREngine` Class**: Wraps the PaddleOCR initialization.
*   **`process_frame(frame, ...)`**:
    1.  Runs PaddleOCR on the full frame.
    2.  Iterates through every detected text box.
    3.  **`is_inside_roi(box, roi)`**: Uses Shapely to check if the center of a text box is inside a defining ROI polygon.
    4.  **Grouping**: Assigns text to "ROI_1" (Header), "ROI_2" (Value), etc.
    5.  **Decimal Fixing**: Converts `34567` to `345.67` based on digit count (heuristic).

#### D. The "Main Loop" (Video Mode)
This is where the business logic lives:
1.  **Load Video**: Checks for valid file and dimensions.
2.  **Header Detection**: On the **first frame** only, it grabs text from ROI 1 & 3 to use as CSV headers (e.g., "Volume", "Flow").
3.  **Confirmation Logic (The 2-step check)**:
    *   *Input:* Current reading `R`.
    *   *State:* Tracked value `T`.
    *   **Logic:**
        *   If `R == 0`: **RESET** tracker (ignore zeros).
        *   If `R != T`: **UPDATE** tracker to `R` (Wait for confirmation).
        *   If `R == T` (Appears twice in a row): **CONFIRM** and **SAVE** to CSV.
4.  **Validation (Ollama)**: 
    *   Every `n` seconds, sends the frame to `ollama_validator.py` to get independent reading.
    *   Logs validation status (MATCH, CORRECTED, or FILLED) in the CSV.

---

### `ollama_validator.py` - The AI Interface

#### `OllamaValidator` Class
*   **`frame_to_base64(frame)`**: Encodes OpenCV image to Base64 string for API transmission.
*   **`validate_meter_reading(...)`**:
    *   Constructs a prompt: *"Look at this meter... return ONLY the number."*
    *   Sends HTTP POST request to `localhost:11434`.
    *   Parses response using Regex to find numbers.
    *   Returns the value to `ocr.py` for cross-referencing.

---

## 7. 🧠 Key Algorithms Explained

### 1. ROI Scaling Algorithm
The system is resolution-independent.
$$ X_{new} = X_{ref} \times \frac{Width_{video}}{6000} $$
$$ Y_{new} = Y_{ref} \times \frac{Height_{video}}{3610} $$
This ensures that even if the video is resized, the ROIs still target the correct screen areas.

### 2. Temporal Confirmation State Machine
This logic eliminates "flicker" errors (e.g., specific frames where `8` looks like `B`).
*   **State 0 (Tracking)**: A new number appears. We suspect it might be noise.
*   **State 1 (Confirmed)**: The *exact same* number appears in the next frame. It is now treated as a valid reading and saved.
*   **State 2 (Stable)**: The number continues to appear. We ignore these redundant frames to keep CSV size small.
*   **Reset**: If the number changes or becomes zero, we reset to State 0.

### 3. CSV Dynamic Header Construction
Instead of hardcoding "Column 1", the script reads the text inside the Label ROIs (ROI_1 and ROI_3) to dynamically name the columns in the output CSV. This makes the data self-documenting.

---

## 8. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Could not open video file"** | Invalid path or double extension. | Check path. Watch out for `.mp4.mp4`. |
| **"Video dimensions are 0x0"** | Corrupt file or codec issue. | Ensure video plays in VLC/Media Player. |
| **Ollama validation failed** | Ollama not running or model missing. | Run `start_ollama.bat` or `ollama pull llava`. |
| **CSV headers are empty** | First frame was blurry/blank. | Ensure video starts with clear view of meter. |
| **PaddleOCR import error** | Version mismatch. | The script auto-applies a patch, but ensure Python 3.10 is used. |

---
**Document Generated:** 2025-12-15
**Author:** Antigravity AI Assistant
