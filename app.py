import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from google.cloud import bigquery

from fetch_data_from_bigquery import fetch_data_from_bigquery
from generate_heatmap import generate_heatmap

def main(bq_client):
    st.title("Gym Locker Assignment Analysis")

    # Fetch data and generate heatmaps
    images_700_fit, images_sweat = fetch_data_from_bigquery(bq_client)
    heatmap_data_700_fit = generate_heatmap(images_700_fit)
    heatmap_data_sweat = generate_heatmap(images_sweat, nr_lockers=160)

    tab1, tab2 = st.tabs(["700 Fit", "Sweat"])

    with tab1:
        annotations = np.arange(1, 163).reshape(18, 9)
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data_700_fit, annot=annotations, cbar=True, fmt="d")
        plt.title("Locker Usage Heatmap (700 Fit)")
        plt.xlabel("Locker Number")
        plt.xticks([])
        plt.yticks([])
        st.pyplot(plt)

    with tab2:
        annotations2 = np.arange(1, 161).reshape(16, 10)
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data_sweat, annot=annotations2, cbar=True, fmt="d")
        plt.title("Locker Usage Heatmap (Sweat)")
        plt.xlabel("Locker Number")
        plt.xticks([])
        plt.yticks([])
        st.pyplot(plt)

if __name__ == "__main__":
    bq_client = bigquery.Client()
    main(bq_client)
