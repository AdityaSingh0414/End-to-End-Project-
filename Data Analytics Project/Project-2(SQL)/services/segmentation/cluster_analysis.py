import pandas as pd

def analyze_clusters(df_clustered, features):
    """Analyzes the characteristics of each cluster."""
    if 'Cluster' not in df_clustered:
        return None
        
    # Group by cluster and calculate mean for the features
    summary = df_clustered.groupby('Cluster')[features].mean().reset_index()
    
    # Simple labeling logic based on the first feature
    if not features:
        return summary
        
    sorted_clusters = summary.sort_values(by=features[0], ascending=False)['Cluster'].tolist()
    labels = ['High Value', 'Medium Value', 'Low Value']
    
    label_map = {}
    for i, cluster in enumerate(sorted_clusters):
        label_map[cluster] = labels[i] if i < len(labels) else f"Segment {i}"
        
    summary['Segment Label'] = summary['Cluster'].map(label_map)
    df_clustered['Segment Label'] = df_clustered['Cluster'].map(label_map)
    
    return summary
