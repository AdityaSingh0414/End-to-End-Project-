import streamlit as st
import sys
import os

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.session_manager import init_session_state, get_history, add_to_history, clear_history
from services.text_to_sql.sql_generator import generate_sql
from services.text_to_sql.sql_validator import is_safe_sql
from services.text_to_sql.sql_executor import execute_query, get_schema
from services.text_to_sql.sql_explainer import explain_sql
from core.config import Config

st.set_page_config(page_title="Chat With Data", page_icon="💬", layout="wide")
init_session_state()

st.title("💬 Chat With Data")
st.markdown("Ask natural language questions about your database.")

# Sidebar for options
with st.sidebar:
    st.header("Settings")
    use_postgres = st.checkbox("Use PostgreSQL", value=False)
    if st.button("Clear Chat"):
        clear_history()
        st.rerun()
        
    if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == "your_groq_api_key_here":
        st.warning("Please configure GROQ_API_KEY in .env")

# Display chat history
for message in get_history():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message:
            st.dataframe(message["data"])
        if "sql" in message:
            with st.expander("View SQL"):
                st.code(message["sql"], language="sql")
        if "explanation" in message:
            st.info(message["explanation"])

# User input
if prompt := st.chat_input("E.g., Show top 10 customers by revenue"):
    # Add user message to history
    add_to_history("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating SQL..."):
            schema = get_schema(use_postgres)
            sql_query = generate_sql(prompt, schema)
            
        with st.expander("Generated SQL Query"):
            st.code(sql_query, language="sql")
            
        is_safe, message_safe = is_safe_sql(sql_query)
        
        if not is_safe:
            st.error(message_safe)
            add_to_history("assistant", message_safe)
        else:
            with st.spinner("Executing Query..."):
                df, err = execute_query(sql_query, use_postgres)
                
            if err:
                st.error(f"Execution Error: {err}")
                add_to_history("assistant", f"Execution Error: {err}")
            else:
                st.dataframe(df)
                
                with st.spinner("Analyzing Results..."):
                    explanation = explain_sql(sql_query)
                st.success(explanation)
                
                # Save to history
                # We update the last history element instead of using a new function 
                # to keep it simple, but we'll just push a new dict.
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "Here are the results of your query:",
                    "data": df,
                    "sql": sql_query,
                    "explanation": explanation
                })
