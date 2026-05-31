from langchain_groq import ChatGroq
from core.config import Config
from core.prompts import SQL_EXPLANATION_PROMPT

def explain_sql(query):
    """Explains the SQL query in plain English."""
    if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "your_groq_api_key_here":
        return "Explanation not available without Groq API Key."
        
    try:
        llm = ChatGroq(temperature=0.3, model_name="llama3-70b-8192", groq_api_key=Config.GROQ_API_KEY)
        prompt = SQL_EXPLANATION_PROMPT.format(query=query)
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error generating explanation: {str(e)}"
