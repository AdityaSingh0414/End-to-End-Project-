from ai_engine.embeddings.embedder import (
    EmbeddingGenerator
)


def test_embedding_generation():

    text = "Artificial Intelligence"

    embedding = (
        EmbeddingGenerator
        .generate_embedding(text)
    )

    assert len(embedding) > 0