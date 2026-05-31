from ai_engine.embeddings.embedder import (
    EmbeddingGenerator
)

from ai_engine.similarity.similarity_engine import (
    SimilarityEngine
)


def test_similarity_score():

    text1 = "Artificial Intelligence"

    text2 = "AI"

    emb1 = (
        EmbeddingGenerator
        .generate_embedding(text1)
    )

    emb2 = (
        EmbeddingGenerator
        .generate_embedding(text2)
    )

    score = (
        SimilarityEngine
        .calculate_similarity(
            emb1,
            emb2
        )
    )

    assert score >= 0