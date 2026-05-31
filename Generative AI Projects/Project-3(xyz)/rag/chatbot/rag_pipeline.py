from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.metrics.pairwise import cosine_similarity

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except Exception:
    faiss = None
    SentenceTransformer = None


ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "rag" / "vector_db" / "faiss.index"
METADATA_PATH = ROOT / "rag" / "vector_db" / "metadata.json"
TFIDF_PATH = ROOT / "rag" / "vector_db" / "tfidf.joblib"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class LocalRAGPipeline:
    def __init__(self) -> None:
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        self.backend = "tfidf"
        if INDEX_PATH.exists() and faiss is not None and SentenceTransformer is not None:
            self.model = SentenceTransformer(MODEL_NAME)
            self.index = faiss.read_index(str(INDEX_PATH))
            self.backend = "faiss"
        else:
            bundle = joblib.load(TFIDF_PATH)
            self.vectorizer = bundle["vectorizer"]
            self.matrix = bundle["matrix"]

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, object]]:
        if self.backend == "faiss":
            query_embedding = self.model.encode([query], normalize_embeddings=True)
            scores, indexes = self.index.search(query_embedding, top_k)
            pairs = zip(scores[0], indexes[0])
        else:
            query_vector = self.vectorizer.transform([query])
            sims = cosine_similarity(query_vector, self.matrix)[0]
            ranked = sims.argsort()[::-1][:top_k]
            pairs = [(sims[idx], idx) for idx in ranked]

        results = []
        for score, idx in pairs:
            if idx == -1:
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)
        return results

    def answer(self, query: str) -> dict[str, object]:
        docs = self.retrieve(query)
        context = "\n\n".join(f"{doc['title']}: {doc['text']}" for doc in docs)
        answer = (
            "Based on the retrieved medical context, "
            f"the most relevant points are: {context}. "
            "Please confirm with a qualified clinician for diagnosis or treatment."
        )
        return {
            "query": query,
            "answer": answer,
            "sources": [{"title": doc["title"], "score": doc["score"]} for doc in docs],
        }
