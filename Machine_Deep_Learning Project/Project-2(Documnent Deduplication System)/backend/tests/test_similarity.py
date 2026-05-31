from ai_engine.preprocessing.text_cleaner import TextCleaner

from ai_engine.embeddings.embedder import (
    EmbeddingGenerator
)

from ai_engine.similarity.similarity_engine import (
    SimilarityEngine
)


def test_similarity():

    text1 = """
    Artificial Intelligence is changing the world.
    """

    text2 = """
    AI is transforming industries worldwide.
    """

    clean1 = TextCleaner.clean(text1)
    clean2 = TextCleaner.clean(text2)

    emb1 = EmbeddingGenerator.generate_embedding(
        clean1
    )

    emb2 = EmbeddingGenerator.generate_embedding(
        clean2
    )

    score = SimilarityEngine.calculate_similarity(
        emb1,
        emb2
    )

    assert score > 0