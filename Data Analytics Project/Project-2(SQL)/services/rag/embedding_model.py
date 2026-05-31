from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_model():
    """Returns the SentenceTransformer embedding model."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
