import pandas as pd
from sqlalchemy import create_engine
from core.config import Config

def execute_query(query, use_postgres=False):
    """Executes the SQL query and returns a Pandas DataFrame."""
    try:
        uri = Config.get_postgres_uri() if use_postgres else Config.SQLITE_URI
        engine = create_engine(uri)
        df = pd.read_sql(query, engine)
        return df, None
    except Exception as e:
        return None, str(e)

def get_schema(use_postgres=False):
    """Retrieves the schema of the database."""
    try:
        uri = Config.get_postgres_uri() if use_postgres else Config.SQLITE_URI
        engine = create_engine(uri)
        
        # Simple schema fetch for SQLite
        if not use_postgres:
            df = pd.read_sql("SELECT name, sql FROM sqlite_master WHERE type='table'", engine)
            schema = "\n".join(df['sql'].dropna().tolist())
            return schema
        else:
            return "Schema generation for Postgres not fully implemented in this sample."
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"
