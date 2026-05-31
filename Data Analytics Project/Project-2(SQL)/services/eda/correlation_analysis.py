import pandas as pd
import numpy as np

def get_correlation_matrix(df):
    """Calculates correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        return numeric_df.corr()
    return None
