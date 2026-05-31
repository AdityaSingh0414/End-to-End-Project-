from ai_engine.embeddings.embedder import (
    EmbeddingGenerator
)

from vector_db.faiss.faiss_manager import (
    FAISSManager
)


class VectorRetriever:

    def __init__(self):

        self.faiss_db = (
            FAISSManager()
        )

    def retrieve(
        self,
        query
    ):

        query_embedding = (
            EmbeddingGenerator
            .generate_embedding(
                query
            )
        )

        return self.faiss_db.search(
            query_embedding
        )