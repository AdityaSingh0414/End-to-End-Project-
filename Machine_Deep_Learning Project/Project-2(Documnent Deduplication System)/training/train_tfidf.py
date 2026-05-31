from sklearn.feature_extraction.text import TfidfVectorizer

class TFIDFTrainer:

    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def train(self, documents):

        vectors = self.vectorizer.fit_transform(
            documents
        )

        return vectors