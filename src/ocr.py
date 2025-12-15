#!/usr/bin/env python3
"""
OCR Pipeline (PaddleOCR Only) + Freeze Detection + ROI Grouping

Features:
- PaddleOCR text detection + recognition
- Auto-ROI clustering (KMeans)
- Video processing
- Freeze detection on ROI_3 for 2–3 sec at 20 FPS
- 95% similarity allowed using Levenshtein ratio
- Saves stable results to CSV
- Annotated video support
"""

import argparse
import os
import sys
import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict

# -------------------------
# CRITICAL: Monkey patch for PaddlePaddle 2.6+ compatibility
# This MUST be done before importing paddleocr
# -------------------------
def apply_paddle_patch():
    try:
        import paddle
        if hasattr(paddle, 'base') and hasattr(paddle.base, 'libpaddle'):
            if hasattr(paddle.base.libpaddle, 'AnalysisConfig'):
                original_class = paddle.base.libpaddle.AnalysisConfig
                if not hasattr(original_class, 'set_optimization_level'):
                    def set_optimization_level(self, level):
                        # Dummy implementation - optimization level is deprecated
                        pass
                    original_class.set_optimization_level = set_optimization_level
                    print("[INFO] Applied PaddlePaddle 2.6+ compatibility patch")
    except Exception as e:
        print(f"[WARN] Could not apply paddle patch: {e}")

# Apply patch immediately
apply_paddle_patch()

import cv2
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, Point, MultiPoint
from sklearn.cluster import KMeans
from difflib import SequenceMatcher

# Excel support (optional)
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    print("[INFO] openpyxl not installed. Excel export disabled. Install with: pip install openpyxl")

# PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except Exception as e:
    print(f"ERROR: PaddleOCR not available: {e}")
    print("Please install: pip install paddleocr")
    sys.exit(1)

# Ollama Validator (optional)
try:
    from ollama_validator import OllamaValidator
    OLLAMA_AVAILABLE = True
except Exception as e:
    print(f"[INFO] Ollama validator not available: {e}")
    OLLAMA_AVAILABLE = False


# ------------------------------------------
# Helpers
# ------------------------------------------
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def similarity(a, b):
    """95% similarity allowed"""
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()

def fix_decimal(text):
    """Convert long numbers like 34567 → 345.67"""
    import re
    if re.fullmatch(r"\d{5,}", text):
        return f"{text[:-2]}.{text[-2:]}"
    return text

def get_hardcoded_rois(target_w=None, target_h=None):
    """
    Return hardcoded static ROI coordinates
    Scales coordinates from reference resolution (6000x3610) to target resolution
    """
    # Reference resolution for the hardcoded coordinates
    REF_W = 6000
    REF_H = 3610

    # Define your static ROI coordinates here (based on REF_W x REF_H)
    # Format: [top-left, top-right, bottom-right, bottom-left]
    STATIC_ROIS = {
        "ROI_1": [
            [1276, 700],
            [2556, 698],
            [2556, 916],
            [1278, 915]
        ],
        "ROI_2": [
            [1272, 941],
            [2554, 941],
            [2553, 1248],
            [1271, 1246]
        ],
        "ROI_3": [
            [1460, 1424],
            [2356, 1423],
            [2355, 1618],
            [1458, 1619]
        ],
        "ROI_4": [
            [1265, 1648],
            [2570, 1649],
            [2573, 1952],
            [1266, 1952]
        ]
    }
    
    scale_x = 1.0
    scale_y = 1.0
    
    if target_w and target_h:
        scale_x = target_w / REF_W
        scale_y = target_h / REF_H
        print(f"[INFO] Scaling ROIs: {REF_W}x{REF_H} -> {target_w}x{target_h} (Sx={scale_x:.3f}, Sy={scale_y:.3f})")
    
    rois = []
    for i in range(1, 5):
        roi_key = f"ROI_{i}"
        if roi_key in STATIC_ROIS:
            coords = STATIC_ROIS[roi_key]
            # Scale coordinates
            scaled_coords = []
            for x, y in coords:
                scaled_coords.append((x * scale_x, y * scale_y))
            
            polygon = Polygon(scaled_coords)
            rois.append(polygon)
        else:
            rois.append(None)
    
    print(f"[INFO] Using hardcoded static ROIs ({len([r for r in rois if r])} regions)")
    return rois

def load_static_rois(config_file):
    """Load static ROI coordinates from JSON config file"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        rois = []
        roi_data = config.get('rois', {})
        
        # Load ROIs in order (ROI_1, ROI_2, ROI_3, ROI_4)
        for i in range(1, 5):
            roi_key = f"ROI_{i}"
            if roi_key in roi_data:
                coords = roi_data[roi_key]
                # Convert to Polygon
                polygon = Polygon(coords)
                rois.append(polygon)
            else:
                rois.append(None)
        
        print(f"[INFO] Loaded {len([r for r in rois if r])} static ROIs from {config_file}")
        return rois
    except FileNotFoundError:
        print(f"[ERROR] ROI config file not found: {config_file}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load ROI config: {e}")
        return None


# ------------------------------------------
# OCR Engine (Paddle Only)
# ------------------------------------------
class OCREngine:
    def __init__(self, langs=["en"]):
        try:
            self.ocr = PaddleOCR(
                lang=langs[0],
                use_textline_orientation=True
            )
        except Exception as e:
            print(f"[WARN] Modern PaddleOCR init failed: {e}")
            try:
                self.ocr = PaddleOCR(
                    lang=langs[0],
                    use_angle_cls=True
                )
            except Exception as e2:
                print(f"[ERROR] All PaddleOCR init attempts failed: {e2}")
                raise e2

    def run(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # cls=True enables orientation classification (optional but good)
        raw = self.ocr.ocr(img_rgb, cls=True)

        # Debug: Print raw output structure if needed
        # print(f"[DEBUG] Raw OCR output: {raw}")

        results = []
        if not raw or raw[0] is None:
            return results

        # PaddleOCR returns [ [line1, line2, ...] ] for a single image
        for line in raw[0]:
            try:
                bbox = line[0]
                text = line[1][0]
                conf = float(line[1][1])
                results.append((bbox, text, conf))
            except Exception as e:
                print(f"[WARN] Failed to parse OCR line: {line} - Error: {e}")
                continue
        return results


# ------------------------------------------
# Auto ROI Clustering
# ------------------------------------------
def auto_cluster_rois(ocr_results, n_rois=4):
    centers = []
    boxes = []
    for bbox, text, conf in ocr_results:
        pts = np.array(bbox, float)
        centers.append([np.mean(pts[:,0]), np.mean(pts[:,1])])
        boxes.append(bbox)

    if not centers:
        return []

    centers = np.array(centers)
    n_clusters = min(n_rois, len(centers))
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(centers)
    labels = kmeans.labels_

    rois = []
    for cid in range(n_clusters):
        pts = []
        for idx,lbl in enumerate(labels):
            if lbl == cid:
                for p in boxes[idx]:
                    pts.append(tuple(map(float,p)))
        if len(pts)>=3:
            rois.append(MultiPoint(pts).convex_hull)
        else:
            rois.append(None)
    return rois


def is_inside_roi(bbox, roi):
    pts = np.array(bbox, float)
    cx = np.mean(pts[:,0])
    cy = np.mean(pts[:,1])
    return roi.contains(Point(cx,cy))


# ------------------------------------------
# Frame Processing
# ------------------------------------------
def process_frame(frame, engine, rois, n_rois):
    ocr_out = engine.run(frame)

    # If ROIs haven't been determined yet (None) or are empty ([]), try to find them
    if rois is None or len(rois) == 0:
        new_rois = auto_cluster_rois(ocr_out, n_rois)
        # Only accept new_rois if we actually found clusters
        if new_rois and len(new_rois) > 0:
            rois = new_rois
            print(f"[INFO] Auto-detected {len(rois)} ROIs.")

    grouped = defaultdict(list)
    for bbox, text, conf in ocr_out:
        print(f"  [DEBUG] Found text: '{text}' (conf: {conf:.2f})")
        assigned = False
        if rois:
            for i, rp in enumerate(rois):
                if rp and is_inside_roi(bbox, rp):
                    grouped[f"ROI_{i+1}"].append(fix_decimal(text))
                    assigned = True
                    break
        if not assigned:
            grouped["UNASSIGNED"].append(text)

    return ocr_out, rois, grouped


# ------------------------------------------
# Main
# ------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--mode", choices=["image","video"], default="video")
    parser.add_argument("--langs", nargs="+", default=["en"])
    parser.add_argument("--n-rois", type=int, default=4)
    parser.add_argument("--out", default="./results")
    parser.add_argument("--frame-skip", type=int, default=0)
    parser.add_argument("--save-annotated-video", action="store_true")
    parser.add_argument("--use-ollama", action="store_true", 
                        help="Enable Ollama validation every 2 seconds")
    parser.add_argument("--validation-interval", type=float, default=2.0,
                        help="Seconds between Ollama validations (default: 2.0)")
    parser.add_argument("--excel", action="store_true",
                        help="Also save results as Excel (.xlsx) files")
    parser.add_argument("--roi-config", type=str, default=None,
                        help="Path to JSON file with static ROI coordinates (e.g., roi_config.json)")
    parser.add_argument("--use-static-rois", action="store_true",
                        help="Use hardcoded static ROI coordinates (defined in code)")
    args = parser.parse_args()

    ensure_dir(args.out)

    engine = OCREngine(langs=args.langs)
    
    # Initialize Ollama validator if requested
    validator = None
    if args.use_ollama:
        if OLLAMA_AVAILABLE:
            try:
                validator = OllamaValidator()
                print(f"[INFO] Ollama validation enabled (interval: {args.validation_interval}s)")
            except Exception as e:
                print(f"[WARN] Could not initialize Ollama: {e}")
                print("[WARN] Continuing without validation...")
        else:
            print("[WARN] --use-ollama specified but ollama_validator not available")
            print("[WARN] Install requests: pip install requests")

    if args.mode == "image":
        # --------------------------------------
        # IMAGE MODE
        # --------------------------------------
        print(f"Processing image: {args.input}")
        
        # Read the image
        frame = cv2.imread(args.input)
        if frame is None:
            print(f"ERROR: Could not read image: {args.input}")
            return
            
        # Load static ROIs (ALWAYS use hardcoded by default)
        if args.roi_config:
            # Config file overrides hardcoded ROIs
            static_rois = load_static_rois(args.roi_config)
        else:
            # Default: Always use hardcoded ROIs (scaled to image size)
            target_h, target_w = frame.shape[:2]
            static_rois = get_hardcoded_rois(target_w, target_h)
        
        # Process the image
        ocr_out, rois, grouped = process_frame(frame, engine, static_rois, args.n_rois)
        
        # Print results to console
        print("\n" + "="*60)
        print("OCR RESULTS")
        print("="*60)
        
        for roi_name in sorted(grouped.keys()):
            if roi_name != "UNASSIGNED":
                values = grouped[roi_name]
                print(f"{roi_name}: {', '.join(values) if values else '(empty)'}")
        
        if grouped.get("UNASSIGNED"):
            print(f"UNASSIGNED: {', '.join(grouped['UNASSIGNED'])}")
        
        # Ollama validation if enabled
        if validator:
            print("\n" + "="*60)
            print("OLLAMA VALIDATION")
            print("="*60)
            result = validator.validate_meter_reading(frame, roi_name="ROI_3")
            if result['value']:
                print(f"Ollama detected: {result['value']}")
                print(f"Raw response: {result.get('raw_response', '')}")
            else:
                print("Ollama validation failed")
        
        # Save results to JSON
        output_json = os.path.join(args.out, f"image_results_{timestamp()}.json")
        results_dict = {
            "image": args.input,
            "timestamp": datetime.now().isoformat(),
            "ocr_results": {k: v for k, v in grouped.items()},
            "rois_detected": len(rois) if rois else 0
        }
        
        if validator and result['value']:
            results_dict["ollama_validation"] = {
                "value": result['value'],
                "confidence": result['confidence'],
                "raw_response": result.get('raw_response', '')
            }
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2, ensure_ascii=False)
        
        # Also save to CSV with ROI_1 and ROI_3 as headers
        output_csv = os.path.join(args.out, f"image_results_{timestamp()}.csv")
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # Get header names from ROI_1 and ROI_3
            r1 = ', '.join(grouped.get("ROI_1", [])) or "Header_1"
            r3 = ', '.join(grouped.get("ROI_3", [])) or "Header_2"
            
            # Get values from ROI_2 and ROI_4
            r2 = ', '.join(grouped.get("ROI_2", []))
            r4 = ', '.join(grouped.get("ROI_4", []))
            
            # Header row: Use ROI_1 and ROI_3 text as column names
            if validator:
                writer.writerow(["Image", r1, r3, "Other_Text", f"Ollama_{r3}"])
            else:
                writer.writerow(["Image", r1, r3, "Other_Text"])
            
            # Data row: ROI_2 and ROI_4 values
            other = ', '.join(grouped.get("UNASSIGNED", []))
            
            if validator and result.get('value'):
                writer.writerow([args.input, r2, r4, other, result['value']])
            else:
                writer.writerow([args.input, r2, r4, other])
        
        # Save annotated image
        annotated_img = frame.copy()
        
        # Draw bounding boxes and text for each OCR result
        for bbox, text, conf in ocr_out:
            # Convert bbox to integer points
            pts = np.array(bbox, dtype=np.int32)
            
            # Determine which ROI this belongs to
            roi_label = "?"
            if rois:
                for i, rp in enumerate(rois):
                    if rp and is_inside_roi(bbox, rp):
                        roi_label = f"ROI_{i+1}"
                        break
            
            # Draw bounding box
            cv2.polylines(annotated_img, [pts], True, (0, 255, 0), 2)
            
            # Draw text and confidence
            x, y = int(pts[0][0]), int(pts[0][1]) - 10
            label = f"{text} ({conf:.2f})"
            cv2.putText(annotated_img, label, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw ROI label
            cv2.putText(annotated_img, roi_label, (x, y - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # Draw ROI boundaries if detected
        if rois:
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Different colors for each ROI
            for i, roi in enumerate(rois):
                if roi and hasattr(roi, 'exterior'):
                    coords = np.array(roi.exterior.coords, dtype=np.int32)
                    cv2.polylines(annotated_img, [coords], True, colors[i % len(colors)], 3)
                    # Label the ROI
                    centroid = roi.centroid
                    cv2.putText(annotated_img, f"ROI_{i+1}", 
                               (int(centroid.x), int(centroid.y)),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, colors[i % len(colors)], 2)
        
        # Save annotated image
        output_img = os.path.join(args.out, f"annotated_{timestamp()}.jpg")
        cv2.imwrite(output_img, annotated_img)
        
        print("\n" + "="*60)
        print(f"JSON results: {output_json}")
        print(f"CSV results: {output_csv}")
        print(f"Annotated image: {output_img}")
        print("="*60)
        return

    # --------------------------------------
    # VIDEO MODE
    # --------------------------------------
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print(f"[ERROR] Could not open video file: {args.input}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 20
    width  = int(cap.get( cv2.CAP_PROP_FRAME_WIDTH ))
    height = int(cap.get( cv2.CAP_PROP_FRAME_HEIGHT ))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO] Video loaded: {width}x{height} @ {fps:.2f}fps ({total_frames} frames)")

    if width == 0 or height == 0:
        print("[ERROR] Video dimensions are 0x0. Please check the video file.")
        return

    # Load static ROIs (ALWAYS use hardcoded by default)
    if args.roi_config:
        # Config file overrides hardcoded ROIs
        static_rois = load_static_rois(args.roi_config)
    else:
        # Default: Always use hardcoded ROIs (scaled to video size)
        static_rois = get_hardcoded_rois(width, height)

    out_video = None
    if args.save_annotated_video:
        out_path = os.path.join(args.out, f"annotated_{timestamp()}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_video = cv2.VideoWriter(out_path, fourcc, fps, (width,height))
        print("Annotated video:", out_path)

    # Freeze detection settings (optional - we'll save all frames now)
    FREEZE_THRESHOLD = int(fps * 2.5)   # ~50 frames
    last_roi3_text = None
    stable_counter = 0
    start_time = None

    # Create TWO CSV files: one for all frames, one for stable values
    all_frames_csv_path = os.path.join(args.out, f"all_frames_{timestamp()}.csv")
    stable_csv_path = os.path.join(args.out, f"stable_values_{timestamp()}.csv")
    
    all_frames_file = open(all_frames_csv_path, "w", newline="", encoding="utf-8-sig")
    all_writer = csv.writer(all_frames_file)
    
    stable_file = open(stable_csv_path, "w", newline="", encoding="utf-8-sig")
    stable_writer = csv.writer(stable_file)

    rois = static_rois  # Use static ROIs if provided, otherwise None (will auto-detect)
    frame_idx = 0
    last_validation_time = 0.0  # Track when we last validated with Ollama
    
    # Track header names from first frame
    header_roi1 = None
    header_roi3 = None
    headers_written = False
    
    # Confirmation logic: track previous values
    prev_r2 = None
    prev_r4 = None
    confirmed_r2 = None
    confirmed_r4 = None

    print("Processing video...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if args.frame_skip and frame_idx % (args.frame_skip+1)!=0:
            frame_idx += 1
            continue

        ocr_out, rois, grouped = process_frame(frame, engine, rois, args.n_rois)

        # Fetch ROI text safely
        r1 = grouped.get("ROI_1", [""])[0] if grouped.get("ROI_1") else ""
        r2 = grouped.get("ROI_2", [""])[0] if grouped.get("ROI_2") else ""
        r3 = grouped.get("ROI_3", [""])[0] if grouped.get("ROI_3") else ""
        r4 = grouped.get("ROI_4", [""])[0] if grouped.get("ROI_4") else ""
        
        # Collect all unassigned text
        other_text = " | ".join(grouped.get("UNASSIGNED", []))

        current_time = frame_idx / fps
        
        # Write CSV headers from first frame (ROI_1 and ROI_3 become column names)
        if not headers_written:
            header_roi1 = r1 if r1 else "Header_1"
            header_roi3 = r3 if r3 else "Header_2"
            
            # Write headers for all_frames CSV
            if validator:
                all_writer.writerow(["frame_idx", "time_sec", header_roi1, header_roi3, "Other_Text", f"Ollama_{header_roi3}", "Validation_Status"])
            else:
                all_writer.writerow(["frame_idx", "time_sec", header_roi1, header_roi3, "Other_Text"])
            
            # Write headers for stable_values CSV
            stable_writer.writerow(["start_time", "end_time", header_roi1, header_roi3])
            
            headers_written = True
            print(f"[INFO] CSV headers set: '{header_roi1}' and '{header_roi3}'")

        # ---- OLLAMA VALIDATION (every N seconds) ----
        ollama_value = ""
        validation_status = ""
        
        if validator and (current_time - last_validation_time) >= args.validation_interval:
            print(f"[VALIDATION] Running Ollama check at {current_time:.2f}s...")
            validation_result = validator.validate_meter_reading(frame, roi_name="ROI_3")
            
            if validation_result['value']:
                ollama_value = validation_result['value']
                
                # Compare with OCR result
                if r3:
                    if similarity(r3, ollama_value) >= 0.90:
                        validation_status = "MATCH"
                        print(f"  ✓ OCR and Ollama agree: {r3}")
                    else:
                        validation_status = "CORRECTED"
                        print(f"  ⚠ Correction: OCR={r3} → Ollama={ollama_value}")
                        r3 = ollama_value  # Use Ollama's value
                else:
                    validation_status = "FILLED"
                    print(f"  + Ollama found value: {ollama_value} (OCR missed it)")
                    r3 = ollama_value
            else:
                validation_status = "FAILED"
                print(f"  ✗ Ollama validation failed")
            
            last_validation_time = current_time

        # ---- CONFIRMATION LOGIC ----
        # Check if values are zero (reset condition)
        is_zero = (r2 in ["0", "0.0", "0.00", ""] and r4 in ["0", "0.0", "0.00", ""])
        
        if is_zero:
            # Reset tracking on zero values
            prev_r2 = None
            prev_r4 = None
            confirmed_r2 = None
            confirmed_r4 = None
            # Don't save zeros to CSV
        else:
            # Check if current values match previous values (confirmation)
            save_to_csv = False
            
            if prev_r2 == r2 and prev_r4 == r4:
                # Second occurrence - values confirmed!
                if confirmed_r2 != r2 or confirmed_r4 != r4:
                    # Not saved yet, save now
                    save_to_csv = True
                    confirmed_r2 = r2
                    confirmed_r4 = r4
                    print(f"[CONFIRMED] Values stable: {r2}, {r4} → SAVING")
                # else: already saved, skip
            else:
                # Values changed, track new values
                prev_r2 = r2
                prev_r4 = r4
                print(f"[TRACKING] New values: {r2}, {r4} (waiting for confirmation)")
            
            # SAVE to CSV only if confirmed
            if save_to_csv:
                if validator:
                    all_writer.writerow([frame_idx, f"{current_time:.2f}", r2, r4, other_text, ollama_value, validation_status])
                else:
                    all_writer.writerow([frame_idx, f"{current_time:.2f}", r2, r4, other_text])

        # ---- FREEZE DETECTION ON ROI_3 (for stable values CSV) ----
        if r3 and last_roi3_text and similarity(r3, last_roi3_text) >= 0.95:
            stable_counter += 1
        else:
            stable_counter = 0
            start_time = current_time
            last_roi3_text = r3

        if stable_counter >= FREEZE_THRESHOLD:
            end_time = current_time

            # save to stable CSV (ROI_2 and ROI_4 are the data values)
            stable_writer.writerow([
                f"{start_time:.2f}", f"{end_time:.2f}", r2, r4
            ])
            print(f"[STABLE] ROI_3='{r3}' from {start_time:.2f}s to {end_time:.2f}s → SAVED")

            stable_counter = 0
            last_roi3_text = None

        # video annotation
        if out_video:
            out_video.write(frame)

        frame_idx += 1
        
        # Print progress every 50 frames
        if frame_idx % 50 == 0:
            print(f"Processed frame {frame_idx} ({current_time:.1f}s) - ROI_3: {r3}")

    cap.release()
    if out_video:
        out_video.release()
    all_frames_file.close()
    stable_file.close()

    # Export to Excel if requested
    excel_files = []
    if args.excel and EXCEL_AVAILABLE:
        print("\n[INFO] Converting to Excel format...")
        try:
            # Convert all_frames CSV to Excel
            all_frames_excel = all_frames_csv_path.replace('.csv', '.xlsx')
            df_all = pd.read_csv(all_frames_csv_path)
            df_all.to_excel(all_frames_excel, index=False, engine='openpyxl')
            excel_files.append(all_frames_excel)
            
            # Convert stable_values CSV to Excel
            stable_excel = stable_csv_path.replace('.csv', '.xlsx')
            df_stable = pd.read_csv(stable_csv_path)
            df_stable.to_excel(stable_excel, index=False, engine='openpyxl')
            excel_files.append(stable_excel)
            
            print("[INFO] Excel files created successfully!")
        except Exception as e:
            print(f"[WARN] Could not create Excel files: {e}")
    elif args.excel and not EXCEL_AVAILABLE:
        print("[WARN] --excel specified but openpyxl not installed")
        print("[WARN] Install with: pip install openpyxl")

    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print(f"All frames CSV: {all_frames_csv_path}")
    print(f"Stable values CSV: {stable_csv_path}")
    if excel_files:
        print(f"\nExcel files:")
        for excel_file in excel_files:
            print(f"  - {excel_file}")
    if out_video:
        print(f"\nAnnotated video: {out_path}")
    print("="*60)


if __name__ == "__main__":
    main()
