import pandas as pd
import numpy as np

def detect_outliers(df):
    """Detects outliers in numeric columns using the IQR method."""
    outliers_dict = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if not outliers.empty:
            outliers_dict[col] = len(outliers)
    return outliers_dict
