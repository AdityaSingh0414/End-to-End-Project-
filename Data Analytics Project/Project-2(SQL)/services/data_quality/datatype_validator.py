import pandas as pd

def validate_datatypes(df):
    """Checks for mixed data types in columns (basic check)."""
    mixed_types = []
    for col in df.columns:
        types = df[col].apply(type).nunique()
        if types > 1:
            mixed_types.append(col)
    return mixed_types
