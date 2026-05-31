import pandas as pd

def check_duplicates(df):
    """Checks for duplicate rows and returns the count and percentage."""
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100
    return {"duplicate_count": int(dup_count), "duplicate_percentage": round(dup_pct, 2)}
