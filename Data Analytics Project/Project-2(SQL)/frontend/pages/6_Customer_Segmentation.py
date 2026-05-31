import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.segmentation.kmeans_segmentation import perform_kmeans
from services.segmentation.cluster_analysis import analyze_clusters
from services.segmentation.cluster_visualization import visualize_clusters

st.set_page_config(page_title="Customer Segmentation", page_icon="👥", layout="wide")

st.title("👥 Customer Segmentation")

uploaded_file = st.file_uploader("Upload Customer Data (CSV)", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        st.sidebar.header("Configuration")
        features = st.sidebar.multiselect("Select Features for Clustering", numeric_cols, default=numeric_cols[:2])
        n_clusters = st.sidebar.slider("Number of Clusters (K)", min_value=2, max_value=10, value=3)
        
        if len(features) >= 2:
            if st.button("Run Segmentation"):
                with st.spinner("Clustering customers..."):
                    df_clustered, kmeans = perform_kmeans(df, features, n_clusters)
                    
                    if kmeans is not None:
                        summary = analyze_clusters(df_clustered, features)
                        
                        st.header("Cluster Profiles")
                        st.dataframe(summary)
                        
                        st.header("Cluster Visualization")
                        # Visualize first two selected features
                        fig = visualize_clusters(df_clustered, features[0], features[1])
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.header("Sample Clustered Data")
                        st.dataframe(df_clustered.head(50))
        else:
            st.warning("Please select at least 2 features for clustering.")
    else:
        st.warning("Dataset must contain at least 2 numeric columns.")
