from rag.loaders.document_loader import (
    DocumentLoader
)

from rag.chunking.text_chunker import (
    TextChunker
)

from rag.chains.qa_chain import (
    QAChain
)


class RAGPipeline:

    def process_document(
        self,
        file_path
    ):

        text = (
            DocumentLoader
            .load_document(
                file_path
            )
        )

        chunks = (
            TextChunker
            .chunk_text(
                text
            )
        )

        return chunks

    def answer_question(
        self,
        question,
        context
    ):

        return (
            QAChain
            .generate_answer(
                question,
                context
            )
        )