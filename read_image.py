import cv2
import numpy as np
import pytesseract # Swapped EasyOCR for pytesseract
from PIL import Image # Needed for pytesseract/OpenCV interaction
import sys
import os

# ----------------------------
# TESSERACT CONFIGURATION
# ----------------------------
# Explicitly set the path for Tesseract, common on macOS/Linux setups,
# to avoid issues where the system PATH isn't correctly inherited.
# Adjust this path if Tesseract is installed elsewhere (e.g., M1/M2 Mac default is often /opt/homebrew/bin/tesseract)
tesseract_cmd_path = None
for p in ['/opt/homebrew/bin/tesseract', '/usr/local/bin/tesseract']:
    if os.path.exists(p):
        tesseract_cmd_path = p
        break

if tesseract_cmd_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path
    
# Tesseract PSM 6: Assume a single uniform block of text (ideal for structured labels).
TESSERACT_CONFIG = r'--psm 6'

# ----------------------------
# CONFIG
# ----------------------------
# The script will expect the image path as a command-line argument.
# OUT_PATH variable removed, as it will be generated dynamically based on input.
WHITE_THRESH = 160       # grayscale threshold for white
BOTTOM_START = 0.6       # start at 30% of image height (to focus on the shelf/labels)
BOTTOM_END = 1.0         # end at 70% of image height
MIN_AREA = 2500          # ignore tiny regions
PADDING = 10             # Increased padding slightly for better crops

def extract_labels(image_path):
    """
    Detects white labels in a specific ROI, extracts text using pytesseract,
    and returns a list of extracted labels sorted left-to-right.
    """
    print(f"INFO: Processing image: {image_path}", file=sys.stderr)
    
    # ----------------------------
    # LOAD IMAGE
    # ----------------------------
    img = cv2.imread(image_path)
    if img is None:
        print(f"ERROR: Image not found at path: {image_path}", file=sys.stderr)
        return []

    h, w = img.shape[:2]
    
    # Define the Region of Interest (ROI)
    y0 = int(h * BOTTOM_START)
    y1 = int(h * BOTTOM_END)
    roi = img[y0:y1, :] 
    
    if roi.size == 0:
        print("ERROR: ROI dimensions are zero. Check BOTTOM_START/BOTTOM_END values.", file=sys.stderr)
        return []

    # Dynamic output path
    base_name = os.path.basename(image_path)
    file_root, file_ext = os.path.splitext(base_name)
    dynamic_out_path = f"{file_root}_annotated{file_ext}"

    # ----------------------------
    # CREATE WHITE MASK
    # ----------------------------
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, WHITE_THRESH, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    # ----------------------------
    # FIND WHITE LABEL REGIONS
    # ----------------------------
    num_labels, labels_im, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates = []
    
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        aspect_ratio = h_box / w_box
        if area >= MIN_AREA and 0.5 <= aspect_ratio <= 4.5:
            candidates.append((x, y, w_box, h_box))

    candidates.sort(key=lambda b: b[0])  # left-to-right

    # ----------------------------
    # RUN OCR ON LABELS
    # ----------------------------
    annotated = roi.copy()
    extracted_labels = []  # <-- Collect labels here

    for idx, (x, y, w_box, h_box) in enumerate(candidates, 1):
        x0 = max(0, x - PADDING)
        y0c = max(0, y - PADDING)
        x1 = min(roi.shape[1], x + w_box + PADDING)
        y1c = min(roi.shape[0], y + h_box + PADDING)
        
        crop = roi[y0c:y1c, x0:x1]
        pil_crop = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        
        try:
            extracted_text = pytesseract.image_to_string(pil_crop, config=TESSERACT_CONFIG)
            text = extracted_text.strip().replace('\n', ' ')
        except pytesseract.TesseractNotFoundError:
            print(f"CRITICAL ERROR: Tesseract is not installed or not in PATH.", file=sys.stderr)
            return []
        except Exception as e:
            text = f"OCR Error: {e}"
            print(f"WARNING: Tesseract error on box {idx}: {e}", file=sys.stderr)
        
        if text and "OCR Error" not in text:
            extracted_labels.append(text)
            cv2.rectangle(annotated, (x0, y0c), (x1, y1c), (0,255,0), 2)
            cv2.putText(annotated, text, (x0, max(12,y0c-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        else:
            extracted_labels.append("")  # placeholder for failed OCR
            cv2.rectangle(annotated, (x0, y0c), (x1, y1c), (0,0,255), 1)

    # ----------------------------
    # SAVE IMAGE
    # ----------------------------
    cv2.imwrite(dynamic_out_path, annotated)
    print(f"INFO: Annotated image saved to {dynamic_out_path}", file=sys.stderr)
    
    # ----------------------------
    # RETURN LABELS
    # ----------------------------
    return extracted_labels


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Get image path from command-line argument
        image_path = sys.argv[1]
        extract_labels(image_path)
    else:
        # Fallback to local image.jpg if no argument is provided
        if os.path.exists("image.jpg"):
            print("WARNING: No image path provided. Using default 'image.jpg' in current directory.", file=sys.stderr)
            extract_labels("image.jpg")
        else:
            print("ERROR: No image path provided and 'image.jpg' not found in current directory.", file=sys.stderr)
            print("Usage: python label_detector.py <path/to/image.jpg>", file=sys.stderr)