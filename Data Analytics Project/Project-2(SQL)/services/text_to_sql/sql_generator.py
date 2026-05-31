import os
from langchain_groq import ChatGroq
from core.config import Config
from core.prompts import TEXT_TO_SQL_PROMPT

def generate_sql(question, schema):
    """Generates SQL using Groq Llama 3 based on user question and schema."""
    if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "your_groq_api_key_here":
        return "-- Please set your GROQ_API_KEY in the .env file."
        
    try:
        llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=Config.GROQ_API_KEY)
        prompt = TEXT_TO_SQL_PROMPT.format(schema=schema, question=question)
        response = llm.invoke(prompt)
        return response.content.strip().replace("```sql", "").replace("```", "")
    except Exception as e:
        return f"-- Error generating SQL: {str(e)}"
