import plotly.express as px

def visualize_clusters(df_clustered, x_feature, y_feature):
    """Returns a scatter plot of the clusters."""
    if 'Segment Label' in df_clustered.columns:
        color_col = 'Segment Label'
    elif 'Cluster' in df_clustered.columns:
        color_col = 'Cluster'
    else:
        return None
        
    fig = px.scatter(
        df_clustered, 
        x=x_feature, 
        y=y_feature, 
        color=color_col,
        title=f"Customer Segmentation: {x_feature} vs {y_feature}"
    )
    return fig
