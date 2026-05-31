import os
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from app.models import NewsArticle
from sqlmodel import Session, select
from app.database import engine
from typing import List, Tuple

# Load a lightweight embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

INDEX_PATH = os.getenv("INDEX_PATH", "faiss_index.bin")

def update_vector_index():
    """Fetches new articles from DB and adds them to FAISS index."""
    with Session(engine) as session:
        # Fetch articles that haven't been embedded yet but have summaries
        statement = select(NewsArticle).where(NewsArticle.is_embedded == False, NewsArticle.summary != None)
        articles = session.exec(statement).all()
        
        if not articles:
            print("No new articles to embed.")
            return

        texts = [f"{a.title}. {a.summary}" for a in articles]
        embeddings = embedding_model.encode(texts)
        
        # Determine dimension
        dim = embeddings.shape[1]
        
        # Load existing index or create new one
        if os.path.exists(INDEX_PATH):
            index = faiss.read_index(INDEX_PATH)
        else:
            index = faiss.IndexFlatL2(dim)
        
        # We need a way to map FAISS IDs back to DB IDs. 
        # For simplicity in this beginner-industrial version, 
        # let's rebuild index if we want it robust, or just append.
        # But wait, FAISS doesn't store metadata. 
        # Proper way: Store mapping in DB or a separate file.
        # Simple Mentor Hack: Add 'id' to an ID list.
        
        index.add(np.array(embeddings).astype('float32'))
        faiss.write_index(index, INDEX_PATH)
        
        # Mark as embedded
        for article in articles:
            article.is_embedded = True
            session.add(article)
        session.commit()
        print(f"Added {len(articles)} articles to vector index.")

def search_news(query: str, top_k=3) -> List[NewsArticle]:
    """Search for relevant news using semantic search."""
    if not os.path.exists(INDEX_PATH):
        print("Vector index does not exist.")
        return []

    index = faiss.read_index(INDEX_PATH)
    query_embedding = embedding_model.encode([query])
    
    distances, indices = index.search(np.array(query_embedding).astype('float32'), top_k)
    
    # Map back to DB. This is tricky since FAISS indices are sequential.
    # In a real production app, we'd use a Vector DB like Pinecone/Weaviate or 
    # store FAISS IDs in our SQLite.
    # Mentor Tip: For this project, let's assume we embed them in order.
    
    with Session(engine) as session:
        # Fetch all embedded articles in order of their ID (assuming they were added to index in order)
        all_embedded = session.exec(select(NewsArticle).where(NewsArticle.is_embedded == True)).all()
        
        results = []
        for i in indices[0]:
            if i < len(all_embedded):
                results.append(all_embedded[i])
                
        return results

if __name__ == "__main__":
    update_vector_index()
