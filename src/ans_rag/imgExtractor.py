# import ans_rag.llm as llm
import os
import fitz
def extract_img(path="../samples/ansxx.pdf"):
    PDF_PATH = path
    OUTPUT_FOLDER = "static_img"

    # Create folder if not exists
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Open PDF
    doc = fitz.open(PDF_PATH)

    images=[]

    for page_number in range(len(doc)):
        page = doc[page_number]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"{OUTPUT_FOLDER}/page{page_number+1}_img{img_index+1}.{image_ext}"
            images.append(image_filename)
            with open(image_filename, "wb") as f:
                f.write(image_bytes)

        # print(f"Saved: {image_filename}")
    return images

if __name__=="__main__":
    images=extract_img("../samples/swsw.pdf")
