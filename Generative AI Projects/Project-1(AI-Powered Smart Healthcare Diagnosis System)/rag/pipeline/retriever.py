def retrieve(chunks: list[dict[str, object]], query: str, top_k: int = 3) -> list[dict[str, object]]:
    normalized = query.lower()
    ranked = sorted(chunks, key=lambda item: normalized in item["chunk"].lower(), reverse=True)
    return ranked[:top_k]
