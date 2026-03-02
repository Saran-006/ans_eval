import pdfplumber, re

def clean_text(text):
    # Remove (cid:xxx)
    text = re.sub(r'\(cid:\d+\)', '', text)

    # Remove non-printable control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def get_content_from_pdf(path):
    pdf_path = path

    full_content=""

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # if page_number!=2:continue

            sizer=dict()

            page_height = page.height
            header_limit = page_height * 0.02
            footer_limit = page_height * 0.98
            
            # print(f"\n--- Page {page_number} ---")

            full_content+="\n"
            full_content+=f'\n[Page]'
            full_content+="\n"


            words =page.extract_words(extra_attrs=["fontname", "size"])

            key=[]
            for w in words:
                text = clean_text(w["text"])
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

            b=0
            body=0
            head=0
            for i,j in enumerate(sizer):
                if sizer[j]>b:
                    b=sizer[j]
                    body=j
                if j>head:head=j

            # print(body,head,sep='........')

            liney=0

            for w in words:
                text = clean_text(w["text"])
                font = w["fontname"]
                size = w["size"]
                x0 = w["x0"]
                top = int(w["top"])
                if liney==0:
                    liney=top

                # print(font,size,sep=">>>>")
                
                if not (header_limit < w["top"] < footer_limit):
                    continue
                if int(size)<5:continue

                if top!=liney:
                    text="\n"+text

                full_content+=(text+" ")
                
                liney=top

    return full_content


if __name__=='__main__':
    print(get_content_from_pdf('../samples/qp1.pdf'))

            



            




                
                