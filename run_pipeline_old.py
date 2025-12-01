# New orchestrator: capture photo -> OCR -> sort
import sys
from take_photo import capture_photo
from read_image import extract_labels
from sort_books import sort_call_numbers

def main():
    # 1) take photo
    try:
        imgfile = capture_photo()
    except Exception as e:
        print("Failed to capture photo:", e)
        sys.exit(1)

    # 2) OCR
    try:
        labels, annotated = extract_labels(imgfile)
    except Exception as e:
        print("OCR failed:", e)
        sys.exit(1)

    if not labels:
        print("No labels found.")
        print("Annotated image saved to:", annotated)
        return

    print("OCR labels (left→right):")
    for i, l in enumerate(labels, 1):
        print(f"{i}. {l}")

    # 3) Sort call numbers (best-effort)
    sorted_books = sort_call_numbers(labels)
    print("\nSorted call numbers (best-effort):")
    for i, s in enumerate(sorted_books, 1):
        print(f"{i}. {s}")

if __name__ == "__main__":
    main()