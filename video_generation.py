# generate_sevenseg_display.py
# Requires: pip install opencv-python numpy
import cv2, numpy as np, os, random, math
from pathlib import Path

# ---------- Settings ----------
fps = 30
W, H = 1280, 720
img_path = "c:/Users/niteshk/Desktop/OCR/reader.jpg"   # change if needed
price_per_litre = 1.19

# ROIs (bbox: x1,y1,x2,y2) in 1280x720
bbox1 = (268, 187, 543, 252)   # sale display
bbox2 = (271, 329, 549, 390)   # litres display

# Timing
anim_time = 0.8   # rising animation seconds
hold_time = 5.0   # hold at target seconds
reset_time = 0.2  # reset duration seconds (quick fade)
pause_zero = 2.0  # pause at zero seconds (new requirement)

frames_anim = int(round(anim_time * fps))
frames_hold = int(round(hold_time * fps))
frames_reset = int(round(reset_time * fps))
frames_pause_zero = int(round(pause_zero * fps))

# Targets: 10 random values up to 10000 (2 decimals)
random.seed(42)
targets = [round(random.uniform(0, 10000), 2) for _ in range(10)]

# Output
out_path_mp4 = os.path.expanduser("~/Desktop/fuel_display_1min_sevenseg.mp4")
fourcc_mp4 = cv2.VideoWriter_fourcc(*'mp4v')

# ---------- Utilities: 7-seg renderer ----------
# Segment labeling:
#  -- a --
# |       |
# f       b
# |       |
#  -- g --
# |       |
# e       c
# |       |
#  -- d --   with dot as decimal point

SEGMENTS = {
    '0': (1,1,1,1,1,1,0),
    '1': (0,1,1,0,0,0,0),
    '2': (1,1,0,1,1,0,1),
    '3': (1,1,1,1,0,0,1),
    '4': (0,1,1,0,0,1,1),
    '5': (1,0,1,1,0,1,1),
    '6': (1,0,1,1,1,1,1),
    '7': (1,1,1,0,0,0,0),
    '8': (1,1,1,1,1,1,1),
    '9': (1,1,1,1,0,1,1),
    '-': (0,0,0,0,0,0,1),  # use g segment as minus
    ' ': (0,0,0,0,0,0,0)
}

def draw_sevenseg_digit(img, digit, rect, seg_color=(255,255,255), seg_thickness_ratio=0.13):
    """
    Draws a 7-seg style digit into rect: (x,y,w,h).
    seg_thickness_ratio: fraction of smaller dimension used for segment thickness
    """
    x,y,w,h = rect
    # normalize
    t = int(max(1, round(min(w,h) * seg_thickness_ratio)))  # segment thickness
    # coordinates for segment boxes (approx)
    # We'll draw segments as filled polygons/rectangles with slight rounded corners by drawing rectangles
    # Define key points
    # Horizontal segment length approx w - 2*t
    # Vertical segment height approx (h - 3*t)/2
    a_x1, a_y1 = x + t, y
    a_x2, a_y2 = x + w - t, y + t
    d_x1, d_y1 = a_x1, y + h - t
    d_x2, d_y2 = a_x2, y + h
    g_x1, g_y1 = a_x1, y + (h//2) - (t//2)
    g_x2, g_y2 = a_x2, g_y1 + t

    b_x1, b_y1 = x + w - t, y + t
    b_x2, b_y2 = x + w, y + (h//2) - (t//2)
    c_x1, c_y1 = b_x1, g_y2
    c_x2, c_y2 = b_x2, d_y1 - 1

    f_x1, f_y1 = x, y + t
    f_x2, f_y2 = x + t, (h//2)+y - (t//2)
    e_x1, e_y1 = x, g_y2
    e_x2, e_y2 = x + t, d_y1 - 1

    segs = SEGMENTS.get(digit, SEGMENTS[' '])

    # draw segments if enabled
    if segs[0]:
        cv2.rectangle(img, (a_x1,a_y1),(a_x2,a_y2), seg_color, thickness=-1)
    if segs[1]:
        cv2.rectangle(img, (b_x1,b_y1),(b_x2,b_y2), seg_color, thickness=-1)
    if segs[2]:
        cv2.rectangle(img, (c_x1,c_y1),(c_x2,c_y2), seg_color, thickness=-1)
    if segs[3]:
        cv2.rectangle(img, (d_x1,d_y1),(d_x2,d_y2), seg_color, thickness=-1)
    if segs[4]:
        cv2.rectangle(img, (e_x1,e_y1),(e_x2,e_y2), seg_color, thickness=-1)
    if segs[5]:
        cv2.rectangle(img, (f_x1,f_y1),(f_x2,f_y2), seg_color, thickness=-1)
    if segs[6]:
        cv2.rectangle(img, (g_x1,g_y1),(g_x2,g_y2), seg_color, thickness=-1)

def draw_number_sevenseg(frame, bbox, number_str, seg_color=(255,255,255), spacing_ratio=0.08):
    """
    Draw number_str (e.g. '0123.45') centered inside bbox (x1,y1,x2,y2)
    Uses seven segment digits and draws decimal point as small circle.
    """
    x1,y1,x2,y2 = bbox
    w = x2 - x1
    h = y2 - y1
    # Remove commas; ensure only 0-9, ., -, space
    number_str = str(number_str)
    number_str = number_str.replace(',', '')
    chars = list(number_str)

    # compute width per character dynamically
    # reserve small spacing between digits
    spacing = int(max(1, round(w * spacing_ratio)))
    # estimate digit_width by dividing remaining width by count
    char_count = len(chars)
    if char_count == 0:
        return frame
    digit_w = int((w - (char_count-1)*spacing) / char_count)
    digit_h = h
    # if digit_w too small, reduce char count by allowing smaller scale -> keep digit_w >= 12
    if digit_w < 12:
        digit_w = max(12, digit_w)
    total_width = digit_w*char_count + spacing*(char_count-1)
    start_x = x1 + (w - total_width)//2
    # vertical position top y for digit box
    top_y = y1
    # draw each char
    for i, ch in enumerate(chars):
        dx = start_x + i*(digit_w + spacing)
        dy = top_y
        if ch == '.':
            # draw small circle near bottom-right of previous digit area
            # place dot centered at bottom-right of previous digit rectangle
            dot_r = max(2, digit_w//12)
            cx = dx + dot_r + 2
            cy = y2 - dot_r - 4
            cv2.circle(frame, (cx, cy), dot_r, seg_color, -1)
            continue
        # For safety map unknown char to space
        if ch not in SEGMENTS:
            ch = ' '
        draw_sevenseg_digit(frame, ch, (dx, dy, digit_w, digit_h), seg_color=seg_color)
    return frame

# ---------- Load image ----------
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Cannot load image: {img_path}")
base = cv2.resize(img, (W, H))

# ---------- Video writer ----------
out = cv2.VideoWriter(out_path_mp4, fourcc_mp4, fps, (W, H))
if not out.isOpened():
    print("mp4 writer failed, falling back to AVI.")
    out_path_avi = os.path.expanduser("~/Desktop/fuel_display_1min_sevenseg.avi")
    fourcc_avi = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(out_path_avi, fourcc_avi, fps, (W, H))
    final_out_path = out_path_avi
else:
    final_out_path = out_path_mp4

print("Saving video to:", final_out_path)
print("Targets:", targets)

# ---------- Easing function ----------
def eased_value(t, target):
    # t in [0,1]; quick rise then slow near end using smootherstep-like easing
    # Use combination: cubic ease-out: 1 - (1-t)^3 scaled to target
    return target * (1 - pow(1-t, 3))

# ---------- Frame composition ----------
def compose_frame(sale_val, litres_val):
    frame = base.copy()
    # draw black ROI rectangles
    cv2.rectangle(frame, (bbox1[0], bbox1[1]), (bbox1[2], bbox1[3]), (0,0,0), thickness=-1)
    cv2.rectangle(frame, (bbox2[0], bbox2[1]), (bbox2[2], bbox2[3]), (0,0,0), thickness=-1)
    # Prepare formatted strings (no commas, fixed 2 decimals)
    sale_text = f"{sale_val:.2f}"
    litres_text = f"{litres_val:.2f}"
    # draw using seven-seg
    frame = draw_number_sevenseg(frame, bbox1, sale_text, seg_color=(255,255,255))
    frame = draw_number_sevenseg(frame, bbox2, litres_text, seg_color=(255,255,255))
    return frame

# ---------- Main loop: iterate targets ----------
# initial test frame
out.write(compose_frame(0.0, 0.0))

for target in targets:
    litres_target = target / price_per_litre

    # Rising animation
    for i in range(frames_anim):
        t = i / max(1, frames_anim - 1)
        sale_val = eased_value(t, target)
        litres_val = eased_value(t, litres_target)
        frame = compose_frame(sale_val, litres_val)
        out.write(frame)

    # Hold at exact target
    for _ in range(frames_hold):
        out.write(compose_frame(target, litres_target))

    # Reset to zero with short decay
    for i in range(frames_reset):
        t = i / max(1, frames_reset - 1)
        # linear decay for reset
        sale_val = target * (1 - t)
        litres_val = litres_target * (1 - t)
        out.write(compose_frame(sale_val, litres_val))

    # Pause at zero for specified time
    for _ in range(frames_pause_zero):
        out.write(compose_frame(0.0, 0.0))

# finish
out.release()
print("Done. Video saved to:", final_out_path)
