import os
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv
from app.models import NewsArticle
from sqlmodel import Session, select
from app.database import engine

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def fetch_youtube_news(query="AI news this week"):
    """Fetches latest AI related videos from YouTube."""
    if not YOUTUBE_API_KEY:
        print("YouTube API Key not found. Skipping YouTube scraping.")
        return []

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    # Search for latest videos matching the query
    request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=5,
        order="date",
        type="video"
    )
    response = request.execute()
    
    new_articles = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        link = f"https://www.youtube.com/watch?v={video_id}"
        
        with Session(engine) as session:
            statement = select(NewsArticle).where(NewsArticle.link == link)
            existing = session.exec(statement).first()
            
            if not existing:
                published_str = item["snippet"]["publishedAt"]
                published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                
                article = NewsArticle(
                    title=title,
                    link=link,
                    published_date=published,
                    source="YouTube",
                    content=description
                )
                session.add(article)
                session.commit()
                new_articles.append(article)
                print(f"Added Video: {title}")
                
    return new_articles

if __name__ == "__main__":
    fetch_youtube_news()
