class QAChain:

    @staticmethod
    def generate_answer(
        question,
        context
    ):

        answer = f"""
Question:
{question}

Context:
{context[:300]}
"""

        return answer