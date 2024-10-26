import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from google.cloud import bigquery

from fetch_data_from_bigquery import fetch_data_from_bigquery
from generate_heatmap import generate_heatmap

# Initialize BigQuery client
bq_client = bigquery.Client()


def main(bq_client):
    st.title("Gym Locker Assignment Analysis")

    images_data = fetch_data_from_bigquery(bq_client)
    heatmap_data = generate_heatmap(images_data)
    plt.figure(figsize=(12, 8))
    annotations = np.arange(1, 163).reshape(18, 9)
    sns.heatmap(heatmap_data, annot=annotations, cbar=True, fmt="d")
    plt.title("Locker Usage Heatmap")
    plt.xlabel("Locker Number")
    plt.xticks([])
    plt.yticks([])
    st.pyplot(plt)


if __name__ == "__main__":
    main(bq_client)
