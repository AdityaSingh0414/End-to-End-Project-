from gensim.models import Word2Vec

class Word2VecTrainer:

    def train(self, tokenized_docs):

        model = Word2Vec(
            sentences=tokenized_docs,
            vector_size=100,
            window=5,
            min_count=1
        )

        return model