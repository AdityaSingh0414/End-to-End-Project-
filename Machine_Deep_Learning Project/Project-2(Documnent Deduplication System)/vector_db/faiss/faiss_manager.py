import faiss
import numpy as np


class FAISSManager:

    def __init__(self, dimension=384):

        self.dimension = dimension

        self.index = faiss.IndexFlatL2(
            dimension
        )

    def add_embeddings(
        self,
        embeddings
    ):

        vectors = np.array(
            embeddings
        ).astype("float32")

        self.index.add(vectors)

    def search(
        self,
        query_embedding,
        k=5
    ):

        query = np.array(
            [query_embedding]
        ).astype("float32")

        distances, indices = self.index.search(
            query,
            k
        )

        return distances, indices