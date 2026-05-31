from apscheduler.schedulers.background import BackgroundScheduler
import time
from app.scrapers import rss_scraper
from app.services import llm_service, vector_db
from app.database import init_db

def job():
    print("--- Starting Automation Job ---")
    
    # 1. Scrape
    new_articles = rss_scraper.fetch_rss_news()
    print(f"Scraped {len(new_articles)} new articles.")
    
    # 2. Process with LLM
    llm_service.process_pending_articles()
    
    # 3. Update Vector Index
    vector_db.update_vector_index()
    
    print("--- Job Finished ---")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 6 hours
    scheduler.add_job(job, 'interval', hours=6)
    scheduler.start()
    print("Scheduler started. Running every 6 hours.")

if __name__ == "__main__":
    init_db()
    # Run once immediately
    job()
    # Keep running
    start_scheduler()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pass
