from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.models import NewsArticle
from app.database import get_session, init_db
from app.services import vector_db, llm_service
from app.scrapers import rss_scraper

app = FastAPI(title="AI News Intelligence API")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/news", response_model=List[NewsArticle])
def get_news(session: Session = Depends(get_session)):
    """Fetch all articles from local DB."""
    return session.exec(select(NewsArticle)).all()

@app.post("/scrape")
def trigger_scrape():
    """Trigger the scraping process."""
    new_articles = rss_scraper.fetch_rss_news()
    return {"status": "success", "new_articles_count": len(new_articles)}

@app.get("/chat")
def chat_with_news(query: str):
    """RAG chat endpoint."""
    # 1. Search for relevant news
    relevant_articles = vector_db.search_news(query)
    
    if not relevant_articles:
        return {"answer": "I couldn't find any relevant news articles for your query."}

    # 2. Construct context for LLM
    context = "\n\n".join([f"Title: {a.title}\nSummary: {a.summary}" for a in relevant_articles])
    
    # 3. Use LLM to generate answer (We can reuse llm_service or add a specialized chat func)
    # For now, let's keep it simple
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_template(
        "You are an AI News Assistant. Use the following context to answer the user's question:\n\n"
        "Context:\n{context}\n\n"
        "Question: {query}\n\n"
        "Answer (be concise and cite your sources):"
    )
    
    chain = prompt | llm
    response = chain.invoke({"context": context, "query": query})
    
    return {
        "answer": response.content,
        "sources": [a.title for a in relevant_articles]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
