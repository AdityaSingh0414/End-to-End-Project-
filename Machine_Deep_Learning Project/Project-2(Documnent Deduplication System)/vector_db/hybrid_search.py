from vector_db.faiss.faiss_manager import (
    FAISSManager
)

from vector_db.chromadb.chroma_manager import (
    ChromaManager
)


class HybridSearch:

    def __init__(self):

        self.faiss_db = FAISSManager()

        self.chroma_db = ChromaManager()

    def search(
        self,
        query_embedding
    ):

        faiss_results = (
            self.faiss_db.search(
                query_embedding
            )
        )

        chroma_results = (
            self.chroma_db.search(
                query_embedding
            )
        )

        return {
            "faiss": faiss_results,
            "chromadb": chroma_results
        }