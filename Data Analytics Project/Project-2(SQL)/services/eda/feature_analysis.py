def analyze_features(df):
    """Analyzes features and returns simple column metadata."""
    metadata = []
    for col in df.columns:
        metadata.append({
            'Feature': col,
            'Data Type': str(df[col].dtype),
            'Unique Values': df[col].nunique(),
            'Sample Values': str(df[col].dropna().unique()[:3].tolist())
        })
    return metadata
