import src.notes_rag.chunker as chunker

import src.notes_rag.pdf2txt as pdf

import numpy as np

from sentence_transformers import SentenceTransformer
import config

import pickle


def build_vector_db(path,dbpath):
    content=pdf.get_content_from_pdf(path)

    chunks=chunker.chunk_text(content)


    model = SentenceTransformer(config.EMBEDDING_MODEL)


    #
    texts = [
        "Represent this sentence for retrieval: " +
        chunk["title"] + " " + chunk["content"]
        for chunk in chunks
    ]


    embeddings = model.encode(texts,batch_size=16,normalize_embeddings=True)


    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i]


    with open(dbpath, "wb") as f:
        pickle.dump({
            "chunks": chunks,
            "embeddings": embeddings
        }, f)

    return dbpath

if __name__=='__main__':
    build_vector_db('../samples/bn1.pdf')