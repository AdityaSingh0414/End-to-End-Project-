import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.reporting.pdf_generator import generate_csv, generate_excel, generate_pdf

st.set_page_config(page_title="Report Generator", page_icon="📄", layout="wide")

st.title("📄 Report Generator")

uploaded_file = st.file_uploader("Upload Data for Reporting (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())
    
    filename = st.text_input("Enter filename (without extension)", "Report_1")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Generate CSV"):
            path = generate_csv(df, filename)
            st.success(f"Saved at {path}")
            
    with col2:
        if st.button("Generate Excel"):
            path = generate_excel(df, filename)
            st.success(f"Saved at {path}")
            
    with col3:
        summary_text = st.text_area("Enter Executive Summary for PDF", "This is an automated business insights report.")
        if st.button("Generate PDF"):
            path = generate_pdf(summary_text, filename)
            st.success(f"Saved at {path}")
