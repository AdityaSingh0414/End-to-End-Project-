import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.rag.document_loader import load_document
from services.rag.vector_store import create_vector_store, load_vector_store
from services.rag.retriever import retrieve_context
from services.rag.rag_pipeline import answer_question
from core.config import Config
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="RAG Assistant", page_icon="📚", layout="wide")

st.title("📚 RAG Assistant (Business Glossary)")

st.sidebar.header("Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload a PDF, TXT, or CSV file", type=['pdf', 'txt', 'csv'])

if uploaded_file is not None:
    # Save file temporarily to process
    temp_path = os.path.join("data", "uploads", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    with st.spinner("Processing document..."):
        try:
            docs = load_document(temp_path)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            # Create/Update Vector Store
            create_vector_store(splits)
            st.sidebar.success(f"Successfully processed and embedded {uploaded_file.name}!")
        except Exception as e:
            st.sidebar.error(f"Error processing document: {str(e)}")

st.header("Ask Questions")
if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "your_groq_api_key_here":
    st.warning("Please configure GROQ_API_KEY in .env")
else:
    question = st.text_input("Ask a question about your business dictionary, metrics, or schema:")
    
    if question:
        with st.spinner("Searching for answers..."):
            vs = load_vector_store()
            if vs:
                context = retrieve_context(vs, question)
                if context:
                    answer = answer_question(context, question)
                    st.success("Answer:")
                    st.write(answer)
                    
                    with st.expander("View Retrieved Context"):
                        st.text(context)
                else:
                    st.warning("No relevant context found in uploaded documents.")
            else:
                st.info("Please upload and process a document first to build the knowledge base.")
