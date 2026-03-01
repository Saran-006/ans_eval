import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import sys


with open("vector_db.pkl", "rb") as f:
    data = pickle.load(f)

chunks = data["chunks"]

embeddings = data["embeddings"]

model = SentenceTransformer("BAAI/bge-small-en")


def query_vector_db(query, top_k=3):

    #stopping sysout

    # bge needs this format
    query_text = "Represent this sentence for retrieval: " + query
    
    query_embedding = model.encode(
        [query_text],
        normalize_embeddings=True
    )[0]

    scores = np.dot(embeddings, query_embedding)

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

print(query_vector_db("What is Interruption Case?"))
