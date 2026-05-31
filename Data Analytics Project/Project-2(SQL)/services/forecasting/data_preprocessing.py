import pandas as pd
from sklearn.model_selection import train_test_split

def preprocess_data(df, target_col):
    """Preprocesses data for forecasting."""
    df = df.dropna()
    X = df.select_dtypes(include=['number']).drop(columns=[target_col], errors='ignore')
    y = df[target_col] if target_col in df.columns else None
    
    if y is not None and not X.empty:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        return X_train, X_test, y_train, y_test
    return None, None, None, None
