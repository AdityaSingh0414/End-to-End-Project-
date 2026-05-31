import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AI News Intelligence", layout="wide")

st.title("🤖 AI News Intelligence Aggregator")
st.markdown("---")

# Sidebar for Chat/RAG
with st.sidebar:
    st.header("💬 Chat with AI News")
    user_query = st.text_input("Ask anything about AI news:")
    if user_query:
        with st.spinner("Analyzing news..."):
            try:
                response = requests.get(f"http://localhost:8000/chat?query={user_query}")
                data = response.json()
                st.write("**Answer:**")
                st.info(data["answer"])
                st.write("**Sources:**")
                for src in data.get("sources", []):
                    st.write(f"- {src}")
            except Exception as e:
                st.error("Make sure the FastAPI backend is running!")

# Main Content: Latest News
st.subheader("📰 Latest AI News Feed")

try:
    response = requests.get("http://localhost:8000/news")
    news_data = response.json()
    
    if not news_data:
        st.info("No news found. Try clicking 'Refresh News'.")
    else:
        for article in reversed(news_data): # Show latest first
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### [{article['title']}]({article['link']})")
                    st.write(f"**Source:** {article['source']} | **Date:** {article['published_date'][:10]}")
                    st.success(f"**Summary:** {article['summary']}")
                    st.info(f"**Sentiment:** {article['sentiment']} | **Tags:** {article['tags']}")
                with col2:
                    st.button("View Details", key=article['id'])
                st.markdown("---")
except Exception as e:
    st.error("Could not connect to the API. Please start the backend.")

# Refresh Button
if st.button("🔄 Refresh News"):
    requests.post("http://localhost:8000/scrape")
    st.experimental_rerun()
