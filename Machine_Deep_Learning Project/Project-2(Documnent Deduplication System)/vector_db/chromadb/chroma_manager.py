import chromadb


class ChromaManager:

    def __init__(self):

        self.client = chromadb.Client()

        self.collection = (
            self.client.get_or_create_collection(
                name="documents"
            )
        )

    def add_document(
        self,
        doc_id,
        text,
        embedding
    ):

        self.collection.add(
            ids=[str(doc_id)],
            documents=[text],
            embeddings=[embedding.tolist()]
        )

    def search(
        self,
        query_embedding,
        n_results=5
    ):

        return self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=n_results
        )