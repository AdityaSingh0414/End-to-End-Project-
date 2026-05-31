import streamlit as st
import sys
import os

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.constants import APP_NAME, APP_DESCRIPTION
from core.session_manager import init_session_state

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session_state()

st.title(f"Welcome to {APP_NAME}")
st.markdown(f"*{APP_DESCRIPTION}*")
st.markdown("---")

st.markdown("""
### 🚀 Getting Started
Please select a module from the sidebar on the left.

- **Chat With Data**: Use natural language to query your databases.
- **Dashboard**: View dynamic KPI cards and interactive charts.
- **Automated EDA**: Generate comprehensive data profiles automatically.
- **Data Quality**: Detect nulls, duplicates, and anomalies in your datasets.
- **Forecasting**: Predict future trends based on historical data.
- **Customer Segmentation**: Group your customers into distinct segments.
- **RAG Assistant**: Ask questions based on your business glossaries and documents.
- **Report Generator**: Export insights to PDF, Excel, and CSV.
""")

st.info("💡 **Tip**: Start by uploading a dataset in the EDA or Data Quality section, or head over to 'Chat With Data' to query the sample database.")
