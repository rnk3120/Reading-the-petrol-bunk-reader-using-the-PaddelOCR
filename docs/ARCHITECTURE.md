# OCR System Architecture & Logic Flow

This document outlines the technical architecture, technologies, and logical flow of the OCR solution.

## 🏗️ High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Input_Source ["Input Source"]
        V[Video File .mp4] -->|Frame Extraction| CV[OpenCV Engine]
        I[Image File .jpg] -->|Load| CV
    end

    subgraph Processing_Pipeline ["Processing Pipeline"]
        CV -->|1. Pre-processing| RS[ROI Selector]
        
        subgraph ROI_Logic ["ROI Logic"]
            RS -->|Option A: Auto| KM[KMeans Clustering]
            RS -->|Option B: Static| SP[Static Polygons (Shapely)]
            SP -->|Scale| SC[Resolution Scaler]
        end

        SC -->|2. Cropped Regions| POCR[PaddleOCR Engine]
        KM -->|2. Cropped Regions| POCR

        subgraph Detection_Engine ["AI / Deep Learning Core"]
            POCR -->|Detection (DB)| DET[Text Detector (CNN)]
            DET -->|Recognition (SVTR)| REC[Text Recognizer (RNN)]
        end
    end

    subgraph Validation_Layer ["Validation Layer (Optional)"]
        REC -- "Check every 2s" --> OLL[Ollama Service]
        OLL -->|LLaVA VLM| LLM[Visual Language Model]
        LLM -->|Correction/Verify| VAL[Validation Logic]
    end

    subgraph Business_Logic ["Business Logic & Filtering"]
        REC -->|Raw Text| FL[Filter Logic]
        VAL -.->|Correction| FL
        
        FL -->|Comparision| SC[Stability Check]
        SC -->|"Levenshtein > 95%"| CONF[Confirmation Logic]
        CONF -->|"2nd consecutive occurance"| SAVE[Save Data]
    end

    subgraph Data_Storage ["Data Output"]
        SAVE --> CSV[CSV Files]
        SAVE --> JSON[JSON Metadata]
        SAVE --> IMG[Annotated Media]
        SAVE --> XLS[Excel Report]
    end
```

---

## 🛠️ Technologies Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **OCR Engine** | **PaddleOCR** (Baidu) | Industrial-grade deep learning model for text detection and recognition. Uses ResNet/MobileNet backbones. |
| **Validation AI** | **Ollama + LLaVA** | Local Large Vision-Language Model (LLM) to "see" and "reason" about the image for error correction. |
| **Image Proc** | **OpenCV** (`cv2`) | Video decoding, frame extraction, drawing annotations, and image pre-processing. |
| **Geometry** | **Shapely** | Handling polygon operations to check if detected text falls inside specific Regions of Interest (ROIs). |
| **Data Logic** | **Pandas / NumPy** | Data structuring, matrix operations, and Excel export. |
| **Stabilization** | **Difflib** | Fuzzy string matching (Levenshtein distance) to ignore minor OCR flickers (e.g., `8` vs `B`). |
| **Clustering** | **Scikit-Learn** | (Auto-mode only) KMeans clustering to automatically group text into regions if no static ROIs are provided. |

---

## 🧠 Core Logic Breakdown

### 1. Scaling & ROI Mapping
- **Problem:** Video resolution (e.g., 1280x720) might differ from the reference coordinates (6000x3610).
- **Solution:** We calculate `scale_x = target_w / ref_w` and `scale_y = target_h / ref_h`. All hardcoded polygon points are multiplied by these scalars before processing.

### 2. The Confirmation Algorithm (The "2-Step Check")
To prevent saving flickering or noisy data, we use a specific state machine:
1.  **Detect Value:** `266.58` (Frame 1) -> **Status:** `TRACKING` (Cache this value).
2.  **Verify Next Frame:** `266.58` (Frame 2) -> **Compare:** Matches Cached?
    *   **Yes:** **Status:** `CONFIRMED` -> **SAVE to CSV**.
    *   **No:** Reset & Track new value.
3.  **Ignore Duplicates:** If Frame 3 is also `266.58`, we skip saving because we already recorded this stable state.

### 3. Header/Value Extraction Logic
- **Header Detection:** The script grabs the text from **ROI_1** and **ROI_3** on the *very first* frame. These become the CSV Column Headers (e.g., "Total Volume", "Flow Rate").
- **Data Extraction:** For every subsequent frame, it takes the values from **ROI_2** and **ROI_4** and puts them under those headers.

### 4. Zero-Reset Logic
- If the OCR reads `0` or `0.00`, checking against previous values might incorrectly "confirm" a bad reading during a screen refresh interval.
- **Logic:** If `value == 0`, we force a **Hard Reset** of the tracking state. We wait for the next non-zero number to restart the confirmation cycle.

---

## 🚀 Directory Structure (Generated)

```
OCR/
├── ocr.py                 # Main application logic
├── ollama_validator.py    # AI Interface (LLM)
├── roi_config.json        # (Optional) External ROI coordinates
├── results/               
│   ├── all_frames_*.csv   # Raw verified data
│   ├── stable_values_*.csv# Summarized stable periods
│   └── annotated_*.jpg    # Visual proof
```
