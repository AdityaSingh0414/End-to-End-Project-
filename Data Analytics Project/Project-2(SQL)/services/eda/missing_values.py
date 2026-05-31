import pandas as pd

def get_missing_values(df):
    """Returns missing value counts and percentages."""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({'Missing Values': missing, 'Percentage': missing_pct})
    return missing_df[missing_df['Missing Values'] > 0].sort_values(by='Missing Values', ascending=False)
