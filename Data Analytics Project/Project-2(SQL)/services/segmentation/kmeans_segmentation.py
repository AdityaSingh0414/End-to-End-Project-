from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

def perform_kmeans(df, features, n_clusters=3):
    """Performs KMeans clustering on selected features."""
    X = df[features].dropna()
    if X.empty:
        return df, None
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Assign back to original dataframe (for the rows that were not dropped)
    df_clustered = df.loc[X.index].copy()
    df_clustered['Cluster'] = clusters
    return df_clustered, kmeans
