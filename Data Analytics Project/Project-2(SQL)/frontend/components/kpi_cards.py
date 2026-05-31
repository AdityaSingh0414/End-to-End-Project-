import streamlit as st

def render_kpi(label, value, prefix="", suffix=""):
    """Renders a simple metric KPI card."""
    st.metric(label=label, value=f"{prefix}{value}{suffix}")
