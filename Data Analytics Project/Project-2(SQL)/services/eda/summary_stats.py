import pandas as pd

def get_summary_stats(df):
    """Returns descriptive statistics for the dataset."""
    return df.describe(include='all').T
