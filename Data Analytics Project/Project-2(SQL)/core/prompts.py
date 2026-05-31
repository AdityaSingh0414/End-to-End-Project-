TEXT_TO_SQL_PROMPT = """
You are an expert SQL generator. Given a user question and a database schema, write a valid SQL query to answer the question.
Ensure the SQL is safe (no DROP, DELETE, TRUNCATE, ALTER, INSERT, UPDATE). Only use SELECT.

Schema:
{schema}

Question: {question}

Return ONLY the SQL query, without markdown formatting or extra text.
"""

SQL_EXPLANATION_PROMPT = """
You are a helpful data analyst. Explain the following SQL query in simple, plain English that a business user would understand.

SQL Query:
{query}

Explanation:
"""

BUSINESS_INSIGHTS_PROMPT = """
You are an expert business analyst. Given the following data (which was generated from a user's question), provide 3-5 bullet points of key business insights, trends, patterns, or anomalies. Also, provide a short summary.

User Question: {question}
Data:
{data}

Insights:
"""

RAG_PROMPT = """
You are a knowledgeable business assistant. Answer the user's question based ONLY on the provided context. If the answer is not in the context, say "I don't know based on the provided documents."

Context:
{context}

Question: {question}

Answer:
"""
