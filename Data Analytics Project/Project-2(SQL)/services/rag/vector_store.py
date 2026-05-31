from langchain_community.vectorstores import FAISS
from services.rag.embedding_model import get_embedding_model
import os

FAISS_INDEX_PATH = os.path.join("vector_store", "faiss_index")

def create_vector_store(documents):
    """Creates and saves a FAISS vector store."""
    embeddings = get_embedding_model()
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    return vector_store
    
def load_vector_store():
    """Loads an existing FAISS vector store."""
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(os.path.join(FAISS_INDEX_PATH, "index.faiss")):
        embeddings = get_embedding_model()
        return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return None
