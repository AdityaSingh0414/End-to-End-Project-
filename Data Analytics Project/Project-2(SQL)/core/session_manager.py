import streamlit as st

def init_session_state():
    """Initializes standard session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "current_dataset" not in st.session_state:
        st.session_state.current_dataset = None
        
    if "db_connection" not in st.session_state:
        st.session_state.db_connection = "SQLite (Sample Data)"

def add_to_history(role, content):
    st.session_state.chat_history.append({"role": role, "content": content})
    
def get_history():
    return st.session_state.chat_history
    
def clear_history():
    st.session_state.chat_history = []
