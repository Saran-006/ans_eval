import pdfplumber

pdf_path = "samples/s3.pdf"

full_content=[]

with pdfplumber.open(pdf_path) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):
        # if page_number!=14:continue

        sizer=dict()

        page_height = page.height
        header_limit = page_height * 0.02
        footer_limit = page_height * 0.98
        
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

        b=0
        body=0
        head=0
        for i,j in enumerate(sizer):
            if sizer[j]>b:
                b=sizer[j]
                body=j
            if j>head:head=j

        print(body,head,sep='........')
        ltype=0
        liney=0
        gettype=0
        for w in words:
            text = w["text"]
            font = w["fontname"]
            size = w["size"]
            x0 = w["x0"]
            top = int(w["top"])
            if liney==0:
                liney=top
                gettype=1

            # print(font,size,sep=">>>>")
            if not (header_limit < w["top"] < footer_limit):
                continue
            if int(size)<5:continue

            if top!=liney:
                print()
                gettype=1
            
            if gettype==1:
                if ('Bold' in font):
                    ltype=1
                elif abs(int(size)-body)<=1:
                    ltype=2
                elif (abs(int(size)-head)<=1 or ':' in text):
                    ltype=1
                else:ltype=3
                    
            
            
            if ('Bold' in font) and ltype==1:
                print(f'\x1b[032m{text}\x1b[0m',end=' ')

            elif abs(int(size)-body)<=1 and ltype!=1:
                print(f'\x1b[031m{text}\x1b[0m',end=' ')

            elif (abs(int(size)-head)<=1 or ':' in text):
                print(f'\x1b[032m{text}\x1b[0m',end=' ')
            else:
                print(f'\x1b[033m{text}\x1b[0m',end=' ')


            liney=top
            gettype=0

        



           




            
            