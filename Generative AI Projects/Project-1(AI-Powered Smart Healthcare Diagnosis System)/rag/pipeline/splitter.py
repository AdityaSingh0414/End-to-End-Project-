def split_documents(documents: list[str], chunk_size: int = 300) -> list[str]:
    chunks = []
    for document in documents:
        for index in range(0, len(document), chunk_size):
            chunks.append(document[index:index + chunk_size])
    return chunks
