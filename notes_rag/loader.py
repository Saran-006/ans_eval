import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en")

class db_container:
    chunks=None
    embeddings=None
    model=None

    def __init__(self,c,e,m):
        self.chunks=c
        self.embeddings=e
        self.model=m

def load_db(path):
    with open(path, "rb") as f:
        data = pickle.load(f)

    chunks = data["chunks"]

    embeddings = data["embeddings"]

    return db_container(chunks,embeddings,model)



def query_vector_db(query,db,top_k=3):

    chunks=db.chunks

    # bge needs this format
    query_text = "Represent this sentence for retrieval: " + query
    
    query_embedding = db.model.encode(
        [query_text],
        normalize_embeddings=True
    )[0]

    scores = np.dot(db.embeddings, query_embedding)

    top_indices = np.argsort(scores)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "id": chunks[idx]["id"],
            "title": chunks[idx]["title"],
            "score": float(scores[idx]),
            "content": chunks[idx]["content"]
        })


    return results

if __name__=='__main__':
    print(query_vector_db(input("enter query:")))
