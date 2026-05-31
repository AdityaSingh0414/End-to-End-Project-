import feedparser
from datetime import datetime
from typing import List
from app.models import NewsArticle
from sqlmodel import Session, select
from app.database import engine

RSS_FEEDS = [
    "https://openai.com/news/rss.xml",
    "https://googleblog.blogspot.com/atom.xml", # Generic but usually has AI
    "https://machinelearning.apple.com/rss.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://feeds.feedburner.com/TechCrunch/" # Good for tech/AI news
]

def fetch_rss_news():
    """Fetches news from hardcoded RSS feeds."""
    new_articles = []
    
    for url in RSS_FEEDS:
        print(f"Fetching from: {url}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # Check if article already exists in DB
            with Session(engine) as session:
                statement = select(NewsArticle).where(NewsArticle.link == entry.link)
                existing = session.exec(statement).first()
                
                if not existing:
                    # Parse date if available
                    published = datetime.utcnow()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    
                    article = NewsArticle(
                        title=entry.title,
                        link=entry.link,
                        published_date=published,
                        source=url.split('/')[2], # Simple way to get domain
                        content=entry.get('summary', entry.get('description', ''))
                    )
                    session.add(article)
                    session.commit()
                    new_articles.append(article)
                    print(f"Added: {entry.title}")
                else:
                    # print(f"Skipping (Already exists): {entry.title}")
                    pass
                    
    return new_articles

if __name__ == "__main__":
    from app.database import init_db
    init_db()
    fetch_rss_news()
