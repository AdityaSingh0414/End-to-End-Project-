import os
import json
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv
from app.models import NewsArticle
from sqlmodel import Session, select
from app.database import engine

load_dotenv()

# We can use Groq or OpenAI
# Groq is great for beginners as it's very fast and has a free tier
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

def process_article_with_llm(article: NewsArticle):
    """Summarizes, tags, and analyzes sentiment of an article."""
    
    # Check if we have an API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GROQ_API_KEY"):
        print("No LLM API keys found. Using placeholder processing.")
        article.summary = article.content[:200] + "..." if article.content else "No content"
        article.sentiment = "Neutral"
        article.set_tags(["AI", "General"])
        return article

    # Using LangChain Structured Output
    response_schemas = [
        ResponseSchema(name="summary", description="A concise 2-sentence summary of the news."),
        ResponseSchema(name="sentiment", description="The sentiment: Positive, Negative, or Neutral."),
        ResponseSchema(name="tags", description="A list of 3-5 relevant keywords/tags.")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_template(
        "Analyze the following AI news article:\n"
        "Title: {title}\n"
        "Content: {content}\n\n"
        "{format_instructions}"
    )

    # Initialize LLM (Change to ChatGroq if using Groq)
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    
    chain = prompt | llm | output_parser

    try:
        result = chain.invoke({
            "title": article.title,
            "content": article.content[:3000], # Trucate for token limits
            "format_instructions": format_instructions
        })
        
        article.summary = result.get("summary")
        article.sentiment = result.get("sentiment")
        article.set_tags(result.get("tags", []))
        
    except Exception as e:
        print(f"Error processing with LLM: {e}")
        # Fallback
        article.summary = "Processing error"
        article.sentiment = "Neutral"
        article.set_tags([])

    return article

def process_pending_articles():
    """Processes all articles that don't have a summary yet."""
    with Session(engine) as session:
        statement = select(NewsArticle).where(NewsArticle.summary == None)
        articles = session.exec(statement).all()
        
        print(f"Processing {len(articles)} articles with AI...")
        for article in articles:
            processed_article = process_article_with_llm(article)
            session.add(processed_article)
            session.commit()
            print(f"Processed: {article.title}")

if __name__ == "__main__":
    process_pending_articles()
