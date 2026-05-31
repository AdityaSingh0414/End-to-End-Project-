def retrieve_context(vector_store, query, k=3):
    """Retrieves relevant documents for a query."""
    if vector_store:
        docs = vector_store.similarity_search(query, k=k)
        return "\n".join([doc.page_content for doc in docs])
    return ""
