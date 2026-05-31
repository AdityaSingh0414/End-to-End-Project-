import time

from ai_engine.embeddings.embedder import (
    EmbeddingGenerator
)

from ai_engine.similarity.similarity_engine import (
    SimilarityEngine
)


def test_similarity_speed():

    text = (
        "Artificial Intelligence"
    )

    emb = (
        EmbeddingGenerator
        .generate_embedding(
            text
        )
    )

    start = time.time()

    SimilarityEngine.calculate_similarity(
        emb,
        emb
    )

    end = time.time()

    execution_time = (
        end - start
    )

    assert execution_time < 1