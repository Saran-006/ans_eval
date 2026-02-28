import pdfplumber

pdf_path = "s2.pdf"

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

        # print(sizer)

        body=0
        head=0
        for i,j in enumerate(sizer):
            if sizer[j]>body:body=j
            if j>head:head=j

        print(body,head,sep='........')

        for w in words:
            text = w["text"]
            font = w["fontname"]
            size = w["size"]
            x0 = w["x0"]
            top = w["top"]
            # print(font)cl
            if not (header_limit < w["top"] < footer_limit):
                continue
            if int(size)<5:continue
            
            if int(size)==body:
                print(f'\x1b[031m{text}\x1b[0m',end=' ')
            elif (int(size)==head or ':' in text or 'Bold' in font):
                print(f'\x1b[032m{text}\x1b[0m',end=' ')
            else:
                print(f'\x1b[033m{text}\x1b[0m',end=' ')

        



           




            
            