# ...existing code...
import cv2
import numpy as np
import easyocr

# ----------------------------
# CONFIG
# ----------------------------
IMAGE_PATH = "image.jpg"
OUT_PATH = "ocr_labels_fast.jpg"
WHITE_THRESH = 160       # grayscale threshold for white
BOTTOM_START = 0.3       # start at 30% of image height
BOTTOM_END = 0.7         # end at 70% of image height
MIN_AREA = 2500          # ignore tiny regions
PADDING = 5

# ----------------------------
# LOAD IMAGE
# ----------------------------
img = cv2.imread(IMAGE_PATH)
if img is None:
    raise SystemExit(f"Image not found: {IMAGE_PATH}")

h, w = img.shape[:2]
y0 = int(h * BOTTOM_START)
y1 = int(h * BOTTOM_END)
roi = img[y0:y1, :]

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

# ----------------------------
# SORT LEFT TO RIGHT
# ----------------------------
candidates.sort(key=lambda b: b[0])  # sort by x-coordinate

# ----------------------------
# INIT OCR
# ----------------------------
reader = easyocr.Reader(['en'], gpu=False)

# ----------------------------
# RUN OCR ON LABELS
# ----------------------------
annotated = roi.copy()
for idx, (x, y, w_box, h_box) in enumerate(candidates, 1):
    x0 = max(0, x-PADDING)
    y0c = max(0, y-PADDING)
    x1 = min(roi.shape[1], x+w_box+PADDING)
    y1c = min(roi.shape[0], y+h_box+PADDING)
    
    crop = roi[y0c:y1c, x0:x1]
    results = reader.readtext(crop, detail=1, paragraph=False)
    
    # draw box and print text
    if results:
        text = " ".join([t[1] for t in results])
        print(f"{idx}. {text}")
        cv2.rectangle(annotated, (x0, y0c), (x1, y1c), (0,255,0), 2)
        cv2.putText(annotated, text, (x0, max(12,y0c-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

# ----------------------------
# SAVE & SHOW RESULT
# ----------------------------
cv2.imwrite(OUT_PATH, annotated)
cv2.imshow("OCR Labels (Left to Right, 60-80%)", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()
# ...existing code...
def extract_labels(image_path: str,
                   out_path: str = None,
                   white_thresh:int = WHITE_THRESH,
                   bottom_start:float = BOTTOM_START,
                   bottom_end:float = BOTTOM_END,
                   min_area:int = MIN_AREA,
                   padding:int = PADDING):
    """
    Run the same pipeline on the provided image_path.
    Returns (labels_list, annotated_image_path)
    labels_list: list of strings found left-to-right
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)

    h, w = img.shape[:2]
    y0 = int(h * bottom_start)
    y1 = int(h * bottom_end)
    roi = img[y0:y1, :]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, white_thresh, 255, cv2.THRESH_BINARY)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    num_labels, labels_im, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates = []
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        aspect_ratio = h_box / w_box if w_box > 0 else 0
        if area >= min_area and 0.5 <= aspect_ratio <= 4.5:
            candidates.append((x, y, w_box, h_box))

    candidates.sort(key=lambda b: b[0])  # left to right

    reader_local = easyocr.Reader(['en'], gpu=False)
    annotated = roi.copy()
    labels = []
    for idx, (x, y, w_box, h_box) in enumerate(candidates, 1):
        x0 = max(0, x-padding)
        y0c = max(0, y-padding)
        x1 = min(roi.shape[1], x+w_box+padding)
        y1c = min(roi.shape[0], y+h_box+padding)

        crop = roi[y0c:y1c, x0:x1]
        results = reader_local.readtext(crop, detail=1, paragraph=False)

        if results:
            text = " ".join([t[1] for t in results]).strip()
            labels.append(text)
            cv2.rectangle(annotated, (x0, y0c), (x1, y1c), (0,255,0), 2)
            cv2.putText(annotated, text, (x0, max(12,y0c-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)

    if out_path is None:
        out_path = image_path.replace(".jpg", "_ocr.jpg")
    cv2.imwrite(out_path, annotated)
    return labels, out_path

if __name__ == "__main__":
    labels, out = extract_labels(IMAGE_PATH, OUT_PATH)
    print("Labels:", labels)