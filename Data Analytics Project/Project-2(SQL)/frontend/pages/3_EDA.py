import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.eda.summary_stats import get_summary_stats
from services.eda.missing_values import get_missing_values
from services.eda.outlier_detection import detect_outliers
from services.eda.correlation_analysis import get_correlation_matrix
from services.eda.feature_analysis import analyze_features

st.set_page_config(page_title="Automated EDA", page_icon="📈", layout="wide")

st.title("📈 Automated Exploratory Data Analysis")

uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    
    st.header("Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    
    st.subheader("Data Preview")
    st.dataframe(df.head())
    
    st.header("Feature Analysis")
    st.table(analyze_features(df))
    
    st.header("Summary Statistics")
    st.dataframe(get_summary_stats(df))
    
    st.header("Missing Values")
    missing_df = get_missing_values(df)
    if not missing_df.empty:
        st.dataframe(missing_df)
    else:
        st.success("No missing values found!")
        
    st.header("Outlier Detection (Numeric Columns)")
    outliers = detect_outliers(df)
    if outliers:
        st.json(outliers)
    else:
        st.success("No significant outliers detected based on IQR.")
        
    st.header("Correlation Matrix")
    corr_matrix = get_correlation_matrix(df)
    if corr_matrix is not None:
        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough numeric columns for correlation.")
