from pdf2image import convert_from_bytes
from .markDownROI import mark_region_all_text
from .text_to_latex import convert_to_latex
from config.database import collection_user_texviewpdf
import cv2
import sys
import os
import shutil
import pytesseract
POPPLER_BIN = r"C:\Program Files\Release-24.08.0-0\poppler-24.08.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

DEBUG_DIR  = "debug_images"
TXT_DIR = "txt_files"


def clear_debug_directory():
    """Clear and refresh the debug directory."""
    if os.path.exists(DEBUG_DIR):
        shutil.rmtree(DEBUG_DIR)
        print(f"Cleared existing debug directory: {DEBUG_DIR}")
    os.makedirs(DEBUG_DIR, exist_ok=True)
    print(f"Created fresh debug directory: {DEBUG_DIR}")


def clear_txt_directory():
    """Clear and refresh the txt directory."""
    if os.path.exists(TXT_DIR):
        shutil.rmtree(TXT_DIR)
        print(f"Cleared existing txt directory: {TXT_DIR}")
    os.makedirs(TXT_DIR, exist_ok=True)
    print(f"Created fresh txt directory: {TXT_DIR}")


def clear_debug_images_only():
    """Clear only the debug images directory without processing any new files."""
    clear_debug_directory()
    clear_txt_directory()
    print("Debug directory cleared - no files to process.")


def pdf_conversion_bytes(pdf_bytes: bytes, doc_id: str , dpi: int = 350):
    clear_debug_directory()
    clear_txt_directory()
    
    pdf_name = "uploaded_pdf"
    txt_file_path = os.path.join(TXT_DIR, f"{pdf_name}.txt")
    prompt_path   = os.path.join(TXT_DIR, "file_prompt.txt")
    latex_file_path = os.path.join(TXT_DIR, f"{pdf_name}.tex")
    
    all_text = []

    # open a file to write the region box enclosed characters
    prompt_file = open(prompt_path, 'w', encoding='utf-8')
    pages = convert_from_bytes( pdf_bytes, dpi=dpi, poppler_path=POPPLER_BIN, use_cropbox=False)
    for i, page in enumerate(pages, start=1):
        jpg_path = os.path.join(DEBUG_DIR, f"pdfConverted_{i:03d}.jpg")
        page.save(jpg_path, "JPEG")
        line = f"Saved page {i} to {jpg_path}"
        print(line)
        prompt_file.write(line + "\n")

        # Process the image to mark regions to now annotate
        annotated, coords = mark_region_all_text(jpg_path)
        out_path = os.path.join(DEBUG_DIR, f"annotated_{i:03d}.jpg")
        cv2.imwrite(out_path, annotated)
        line = f"Annotated page {i}, found {len(coords)} regions in {out_path}"
        print(line)
        prompt_file.write(line + "\n")


        # Reload the original full‑page image (to avoid redrawing rectangles)
        orig = cv2.imread(jpg_path)

        coords_sorted = sorted(coords, key=lambda box: (box[0][1], box[0][0]))
        
        # For each box, crop & OCR
        for ridx, ((x0, y0), (x1, y1)) in enumerate(coords_sorted, start=1):
            # Crop the region of interest (ROI)
            roi = orig[y0:y1, x0:x1]

            # optional: convert to gray + threshold for cleaner OCR
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # simple binary threshold (tweak threshold value to taste)
            _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

            # or adaptive threshold:
            # thresh = cv2.adaptiveThreshold(
            #     gray, 255,
            #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            #     cv2.THRESH_BINARY, 11, 2
            # )

            # run Tesseract on the cropped, thresholded ROI
            text = pytesseract.image_to_string(thresh, config="--oem 3 --psm 6 -l eng").strip()
            divider = "─" * 40
            # build the region text blocks
            block = (
                f"Region {ridx} (y={y0}):\n"
                f"{text}\n"
                f"{divider}"
            )
            print(block)
            prompt_file.write(block + "\n")
            
            if text:
                all_text.append(text)

    # Close the prompt file
    prompt_file.close()
    
    plain_text_content = '\n\n'.join(all_text)
    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write(plain_text_content)
    print(f"Saved extracted text to {txt_file_path}")

    # Convert to LaTeX
    latex_content = convert_to_latex(plain_text_content)
    with open(latex_file_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    print(f"Saved LaTeX code to {latex_file_path}")

    # -- Update the MongoDB document
    result = collection_user_texviewpdf.update_one(
        {"_id": doc_id},
        {"$set": {"text": plain_text_content}}
    )
    if result.matched_count:
        print(f"Updated raw text for document {doc_id}")
    else:
        print(f"No document found with _id={doc_id}")
    # Update loading status??

# ─────── Script entry point ───────
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided - just clear the debug directory
        clear_debug_images_only()
        sys.exit(0)
    
    if len(sys.argv) != 2:
        print("Usage: python pdfMaster.py path/to/your.pdf")
        print("       python pdfMaster.py (to clear debug directory)")
        sys.exit(1)

    pdf_file = sys.argv[1]
    if not os.path.isfile(pdf_file):
        print(f"Error: file not found: {pdf_file}")
        sys.exit(1)

    pdf_conversion(pdf_file)