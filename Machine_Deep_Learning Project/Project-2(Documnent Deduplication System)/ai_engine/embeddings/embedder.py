from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    @classmethod
    def generate_embedding(
        cls,
        text
    ):

        embedding = cls.model.encode(
            text
        )

        return embedding