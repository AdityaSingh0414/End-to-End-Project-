import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.data_quality.duplicate_checker import check_duplicates
from services.data_quality.null_checker import check_nulls
from services.data_quality.datatype_validator import validate_datatypes
from services.data_quality.quality_score import calculate_quality_score

st.set_page_config(page_title="Data Quality", page_icon="🧹", layout="wide")

st.title("🧹 Data Quality Analyzer")

uploaded_file = st.file_uploader("Upload a CSV file for quality check", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.header("Quality Assessment")
    
    dup_info = check_duplicates(df)
    null_info = check_nulls(df)
    mixed_types = validate_datatypes(df)
    
    score = calculate_quality_score(dup_info, null_info, len(mixed_types), len(df.columns))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Data Quality Score", f"{score} / 100")
    col2.metric("Duplicate Rows", f"{dup_info['duplicate_count']} ({dup_info['duplicate_percentage']}%)")
    col3.metric("Total Null Cells", f"{null_info['total_nulls']} ({null_info['null_percentage']}%)")
    
    if score >= 90:
        st.success("Excellent Data Quality!")
    elif score >= 70:
        st.warning("Good Data Quality, but needs some cleaning.")
    else:
        st.error("Poor Data Quality. Extensive cleaning required.")
        
    st.subheader("Data Type Issues")
    if mixed_types:
        st.error(f"Columns with mixed data types: {', '.join(mixed_types)}")
    else:
        st.success("No mixed data types detected.")
        
    st.subheader("Improvement Recommendations")
    if dup_info['duplicate_percentage'] > 0:
        st.write("- Consider removing duplicate rows to avoid skewed analysis.")
    if null_info['null_percentage'] > 0:
        st.write("- Handle missing values using imputation or deletion based on the context.")
    if mixed_types:
        st.write("- Clean columns with mixed data types to ensure consistent processing.")
