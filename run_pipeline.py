import sys
from take_photo import capture_photo
from read_image import extract_labels
from sort_books import sort_call_numbers, find_out_of_order

def main():
    # 1) Take photo
    # The file path of the captured image
    imgfile = None 
    try:
        # Assuming capture_photo() returns the path to the saved image file
        imgfile = capture_photo()
        print(f"Photo captured and saved to: {imgfile}")
    except Exception as e:
        print(f"Failed to capture photo: {e}", file=sys.stderr)
        sys.exit(1)

    # 2) OCR
    extracted_labels = []
    try:
        # extract_labels now returns a single array containing all extracted text
        extracted_labels = extract_labels(imgfile)
    except Exception as e:
        print(f"OCR failed (unexpected error during processing): {e}", file=sys.stderr)
        sys.exit(1)

    # Check for error messages returned by extract_labels (e.g., Tesseract not found)
    for label in extracted_labels:
        if label.startswith("ERROR:") or label.startswith("Error:"):
            print(label, file=sys.stderr)
            sys.exit(1)

    labels = extracted_labels

    if not labels:
        print("No readable text found after OCR.", file=sys.stderr)
        return

    # print("OCR labels found (raw, top-to-bottom):")
    # for i, l in enumerate(labels, 1):
    #     print(f"{i}. {l}")

    # 3) Sort call numbers (best-effort)
    print(find_out_of_order(labels))


if __name__ == "__main__":
    main()