from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SimilarityEngine:

    @staticmethod
    def calculate_similarity(
        embedding1,
        embedding2
    ):

        similarity = cosine_similarity(
            np.array([embedding1]),
            np.array([embedding2])
        )

        return float(
            similarity[0][0]
        )