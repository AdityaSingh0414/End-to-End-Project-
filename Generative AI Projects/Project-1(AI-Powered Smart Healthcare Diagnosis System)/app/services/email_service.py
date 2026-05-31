import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models import NewsArticle
from app.database import engine
from dotenv import load_dotenv

load_dotenv()

def generate_digest_email():
    """Fetches articles from last 24 hours and prepares email body."""
    with Session(engine) as session:
        yesterday = datetime.utcnow() - timedelta(days=1)
        statement = select(NewsArticle).where(NewsArticle.published_date >= yesterday)
        articles = session.exec(statement).all()
        
        if not articles:
            return None, "No news in the last 24 hours."

        html_content = "<h2>AI News Daily Digest</h2>"
        for article in articles:
            html_content += f"""
            <h3><a href='{article.link}'>{article.title}</a></h3>
            <p><strong>Summary:</strong> {article.summary}</p>
            <p><strong>Sentiment:</strong> {article.sentiment} | <strong>Tags:</strong> {article.tags}</p>
            <hr>
            """
        return articles, html_content

def send_email():
    """Sends the generated digest via SMTP."""
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not all([sender_email, sender_password, receiver_email]):
        print("Email configuration missing. Skipping email send.")
        return

    articles, body_html = generate_digest_email()
    if not articles:
        print(body_html)
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = f"AI News Digest - {datetime.now().strftime('%Y-%m-%d')}"
    message["From"] = sender_email
    message["To"] = receiver_email

    part = MIMEText(body_html, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Digest email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
