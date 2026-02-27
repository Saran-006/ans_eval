import pdfplumber

pdf_path = "sample.pdf"

full_content=[]

with pdfplumber.open(pdf_path) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):

        sizer=dict()

        page_height = page.height
        header_limit = page_height * 0.08
        footer_limit = page_height * 0.92
        
        print(f"\n--- Page {page_number} ---")

        words = page.extract_words(
            extra_attrs=["fontname", "size"]
        )

        key=[]
        for w in words:
            text = w["text"]
            font = w["fontname"]
            size = w["size"]
            x0 = w["x0"]
            top = w["top"]
            if not (header_limit < w["top"] < footer_limit):
                continue
            if int(size) in key:
                sizer[int(size)]+=1
            else:
                sizer[int(size)]=1
                key.append(int(size))

        print(sizer)
        for i,j in enumerate(sizer):
            print(j)

            
            