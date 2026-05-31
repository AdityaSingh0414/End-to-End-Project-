from rag.rag_pipeline import (
    RAGPipeline
)

rag = RAGPipeline()

answer = (
    rag.answer_question(
        "What is AI?",
        "Artificial Intelligence is a field of computer science."
    )
)

print(answer)