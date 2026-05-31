import pandas as pd

def check_nulls(df):
    """Checks for null values across the dataframe."""
    null_count = df.isnull().sum().sum()
    total_cells = df.size
    null_pct = (null_count / total_cells) * 100 if total_cells > 0 else 0
    return {"total_nulls": int(null_count), "null_percentage": round(null_pct, 2)}
