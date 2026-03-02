import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# If Windows, uncomment and adjust path:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_PATH = "../samples/swsw.pdf"
OUTPUT_FOLDER = "static_img"

# Create folder if not exists
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Open PDF
doc = fitz.open(PDF_PATH)

image_count = 0

for page_number in range(len(doc)):
    page = doc[page_number]
    image_list = page.get_images(full=True)

    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        image_filename = f"{OUTPUT_FOLDER}/page{page_number+1}_img{img_index+1}.{image_ext}"

        with open(image_filename, "wb") as f:
            f.write(image_bytes)

        print(f"Saved: {image_filename}")

        # Apply OCR
        img = Image.open(image_filename)
        text = pytesseract.image_to_string(img)

        print(f"\n--- OCR Result for {image_filename} ---")
        print(text)
        print("----------------------------------------\n")

        image_count += 1

print(f"Total Images Extracted: {image_count}")