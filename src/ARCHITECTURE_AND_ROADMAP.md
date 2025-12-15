# 🏗️ Architecture, Flowchart & Strategic Roadmap

This document outlines the technical architecture, logical flow, and future roadmap of the Intelligent Meter OCR System.

---

## 1. 📐 System Architecture Flowchart

```mermaid
graph TD
    %% Input Layer
    subgraph Input ["Input Layer"]
        Video[Video Stream / File] --> FrameExtractor[Frame Extraction (OpenCV)]
        Image[Static Image] --> Resize[Resolution Scaling Logic]
        FrameExtractor --> Resize
    end

    %% Pre-processing Layer
    subgraph PreProcessing ["ROI & Pre-processing"]
        Resize --> ROI_Loader[Load Static ROIs]
        ROI_Loader --> Scaler[Scale Coordinates to Resolution]
        Scaler --> Cropper[Crop ROI Regions]
        Cropper --> Enhancer[Image Enhancement (Grayscale/Contrast)]
    end

    %% Processing Layer
    subgraph CoreEngine ["OCR Processing Core"]
        Enhancer --> PaddleDetect[PaddleOCR Detection (DB Net)]
        PaddleDetect --> PaddleRec[PaddleOCR Recognition (SVTR)]
        PaddleRec --> TextExtract{Text Detected?}
    end

    %% Logic Layer
    subgraph BusinessLogic ["Business Logic & Validation"]
        TextExtract -- Yes --> HeaderCheck[Header Detection (ROI 1&3)]
        TextExtract -- No --> SkipFrame[Skip Frame]
        
        HeaderCheck --> DataExtract[Value Extraction (ROI 2&4)]
        DataExtract --> ZeroCheck{Is Value 0?}
        
        ZeroCheck -- Yes --> ResetState[RESET Trackers]
        ZeroCheck -- No --> TrackState[Update Tracker]
        
        TrackState --> ConfirmCheck{Same as Prev Frame?}
        ConfirmCheck -- No --> Wait[Wait for Confirmation]
        
        ConfirmCheck -- Yes --> AI_Trigger{Validation Interval?}
    end

    %% Validation Layer
    subgraph Validation ["AI Validation Layer (Optional)"]
        AI_Trigger -- Yes --> Base64[Encode Image to Base64]
        Base64 --> OllamaRequest[HTTP POST to Ollama]
        OllamaRequest --> LLaVA[LLaVA VLM Processing]
        LLaVA --> AI_Response[AI Reading]
        AI_Response --> Compare[Compare: OCR vs AI]
        Compare --> Correction[Auto-Correction Logic]
    end

    %% Output Layer
    subgraph Output ["Data Output"]
        AI_Trigger -- No --> SaveCSV
        Correction --> SaveCSV
        SaveCSV --> CSV_File[Structured CSV]
        SaveCSV --> Excel_File[Excel Report]
        SaveCSV --> Annotate[Annotated Video/Image]
    end
```

---

## 2. 🌍 Real-World Use Case Comparison

| Feature | This Project (Hybrid OCR) | Traditional Industrial OCR | Cloud API Solutions (Google/AWS) |
| :--- | :--- | :--- | :--- |
| **Cost** | **Free / Low** (Local Hardware) | High (License Fees) | High (Per API Call) |
| **Data Privacy** | **100% Offline/Local** | Local | Data leaves premise |
| **Latency** | **Real-time (>20 FPS)** | Real-time | High Latency (Network) |
| **Flexibility** | **High** (Custom ROIs, AI check) | Low (Rigid templates) | High |
| **Accuracy** | **Very High** (Dual Validation) | High (in ideal lighting) | Very High |
| **Resets** | **Auto-handles 0.00 resets** | Often logs errors | N/A |

### Practical Applications:
1.  **Petrol Bunks:** Automating daily reading logs without manual entry errors.
2.  **Factory Meters:** Monitoring pressure/temperature gauges in legacy factories without IoT sensors.
3.  **Utility Billing:** Digitizing old water/electricity meters for smart billing.

---

## 3. 🚀 Future Enhancements Roadmap

### Phase 1: Edge Deployment (Optimization)
*   **Goal:** Run on low-cost hardware (Raspberry Pi / Jetson Nano).
*   **Action:** Convert PaddleOCR models to **ONNX** or **TensorRT** format for 10x faster inference on edge devices.
*   **Benefit:** Enables a standalone "Smart Camera" device.

### Phase 2: Multi-Camera Support
*   **Goal:** Process feeds from 4-8 cameras simultaneously.
*   **Action:** Implement **Multiprocessing** or **AsyncIO** in Python. Use a queue system (RabbitMQ/Redis) to handle frames from multiple sources.
*   **Benefit:** One server can monitor an entire petrol station or factory floor.

### Phase 3: Cloud & IoT Integration (MQTT)
*   **Goal:** Send data to a central dashboard.
*   **Action:** Add an MQTT Publisher. Instead of just saving CSVs, push JSON data to an IoT Broker (AWS IoT / HiveMQ).
*   **Benefit:** Real-time dashboards, alerts (e.g., "Leak Detected"), and historical analytics.

### Phase 4: Self-Correction Learning
*   **Goal:** Make the system smarter over time.
*   **Action:** When AI (Ollama) corrects PaddleOCR, save that image to a "Training Folder". Periodically retrain (fine-tune) PaddleOCR on these difficult images.
*   **Benefit:** The system adapts to specific lighting/glare conditions of the installation site automatically.

---
**Document Generated:** 2025-12-15
**Author:** Antigravity AI Assistant
