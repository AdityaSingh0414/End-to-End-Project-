from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    import faiss
    from sentence_transformers import SentenceTransformer
except Exception:
    faiss = None
    SentenceTransformer = None


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "rag" / "data" / "medical_knowledge.md"
INDEX_PATH = ROOT / "rag" / "vector_db" / "faiss.index"
METADATA_PATH = ROOT / "rag" / "vector_db" / "metadata.json"
TFIDF_PATH = ROOT / "rag" / "vector_db" / "tfidf.joblib"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def chunk_markdown(text: str) -> list[dict[str, str]]:
    chunks = []
    current_title = "Medical Knowledge"
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                chunks.append({"title": current_title, "text": "\n".join(current_lines).strip()})
            current_title = line.replace("## ", "").strip()
            current_lines = []
        elif line.strip():
            current_lines.append(line)
    if current_lines:
        chunks.append({"title": current_title, "text": "\n".join(current_lines).strip()})
    return chunks


def build_index() -> None:
    chunks = chunk_markdown(SOURCE.read_text(encoding="utf-8"))
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    METADATA_PATH.write_text(json.dumps(chunks, indent=2), encoding="utf-8")

    texts = [chunk["text"] for chunk in chunks]
    if faiss is not None and SentenceTransformer is not None:
        try:
            model = SentenceTransformer(MODEL_NAME)
            embeddings = model.encode(texts, normalize_embeddings=True)
            index = faiss.IndexFlatIP(embeddings.shape[1])
            index.add(embeddings)
            faiss.write_index(index, str(INDEX_PATH))
            print(f"Built FAISS index with {len(chunks)} chunks")
            return
        except Exception as exc:
            print(f"SentenceTransformer/FAISS path unavailable, using TF-IDF fallback: {exc}")

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    joblib.dump({"vectorizer": vectorizer, "matrix": matrix}, TFIDF_PATH)
    print(f"Built TF-IDF fallback index with {len(chunks)} chunks")


if __name__ == "__main__":
    build_index()
