from sentence_transformers import (
    SentenceTransformer
)

class BERTTrainer:

    def __init__(self):

        self.model = (
            SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        )

    def generate_embeddings(
        self,
        documents
    ):

        return self.model.encode(
            documents
        )