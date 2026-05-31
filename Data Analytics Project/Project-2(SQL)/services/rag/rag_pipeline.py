from langchain_groq import ChatGroq
from core.config import Config
from core.prompts import RAG_PROMPT

def answer_question(context, question):
    """Generates an answer using Groq."""
    if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "your_groq_api_key_here":
        return "Please configure Groq API Key."
        
    try:
        llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=Config.GROQ_API_KEY)
        prompt = RAG_PROMPT.format(context=context, question=question)
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
