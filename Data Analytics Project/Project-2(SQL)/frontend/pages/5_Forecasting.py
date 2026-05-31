import streamlit as st
import pandas as pd
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.forecasting.data_preprocessing import preprocess_data
from services.forecasting.train_model import train_forecasting_model
from services.forecasting.predict import predict
from services.forecasting.evaluate import evaluate_model

st.set_page_config(page_title="Forecasting", page_icon="🔮", layout="wide")

st.title("🔮 Time Series & Metric Forecasting")

uploaded_file = st.file_uploader("Upload a CSV file with historical data", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        target_col = st.selectbox("Select Target Column to Forecast", numeric_cols)
        model_type = st.selectbox("Select Model", ["Linear Regression", "Random Forest", "XGBoost"])
        
        if st.button("Run Forecast"):
            with st.spinner("Training model..."):
                X_train, X_test, y_train, y_test = preprocess_data(df, target_col)
                
                if X_train is not None:
                    model = train_forecasting_model(X_train, y_train, model_type)
                    predictions = predict(model, X_test)
                    metrics = evaluate_model(y_test, predictions)
                    
                    st.success("Model trained successfully!")
                    
                    st.header("Evaluation Metrics")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("MAE", round(metrics['MAE'], 2))
                    col2.metric("RMSE", round(metrics['RMSE'], 2))
                    col3.metric("R² Score", round(metrics['R2 Score'], 2))
                    
                    st.header("Actual vs Predicted")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=y_test.values, mode='lines', name='Actual'))
                    fig.add_trace(go.Scatter(y=predictions, mode='lines', name='Predicted'))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Insufficient data for training. Please check your features.")
    else:
        st.warning("No numeric columns found to forecast.")
