import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.visualization.auto_chart_selector import get_best_chart
from frontend.components.kpi_cards import render_kpi

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Interactive Dashboard")

uploaded_file = st.file_uploader("Upload Data (CSV) for Dashboard", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.header("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    # Generic KPIs based on dataset size
    with col1: render_kpi("Total Records", len(df))
    with col2: render_kpi("Total Columns", len(df.columns))
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if numeric_cols:
        with col3: render_kpi(f"Avg {numeric_cols[0]}", round(df[numeric_cols[0]].mean(), 2))
    if len(numeric_cols) > 1:
        with col4: render_kpi(f"Total {numeric_cols[1]}", round(df[numeric_cols[1]].sum(), 2))
        
    st.markdown("---")
    
    st.header("Visualizations")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Auto Chart 1")
        if numeric_cols and categorical_cols:
            fig1 = get_best_chart(df, categorical_cols[0], numeric_cols[0])
            st.plotly_chart(fig1, use_container_width=True, key="chart1")
            
    with c2:
        st.subheader("Auto Chart 2")
        if len(numeric_cols) >= 2:
            fig2 = get_best_chart(df, numeric_cols[0], numeric_cols[1])
            st.plotly_chart(fig2, use_container_width=True, key="chart2")
            
    st.subheader("Custom Explorer")
    x_axis = st.selectbox("Select X Axis", df.columns)
    y_axis = st.selectbox("Select Y Axis", df.columns, index=min(1, len(df.columns)-1))
    
    if st.button("Generate Chart"):
        custom_fig = get_best_chart(df, x_axis, y_axis)
        st.plotly_chart(custom_fig, use_container_width=True, key="custom_chart")
