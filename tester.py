import chunker as chk

import pdf2txt as pdf

content=pdf.get_content_from_pdf('samples/s3.pdf')

chk.chunk_document(content)