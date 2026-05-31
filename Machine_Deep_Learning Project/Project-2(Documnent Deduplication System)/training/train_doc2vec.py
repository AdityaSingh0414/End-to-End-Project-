from gensim.models.doc2vec import (
    Doc2Vec,
    TaggedDocument
)

class Doc2VecTrainer:

    def train(self, documents):

        tagged_docs = [
            TaggedDocument(
                words=doc.split(),
                tags=[str(i)]
            )
            for i, doc in enumerate(documents)
        ]

        model = Doc2Vec(
            tagged_docs,
            vector_size=100,
            epochs=20
        )

        return model