def embed_chunks(chunks: list[str]) -> list[dict[str, object]]:
    return [{"chunk": chunk, "embedding_stub": len(chunk)} for chunk in chunks]
