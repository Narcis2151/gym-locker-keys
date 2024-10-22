from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

from fetch_data_from_bigquery import fetch_data_from_bigquery
from generate_heatmap import generate_heatmap

# Assuming you're using service account credentials
SERVICE_ACCOUNT_FILE = "/Users/narcisfanica/Side-Projects/Gym Locker Keys/gcp_key.json"

# Authenticate using service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Initialize BigQuery and GCS clients
bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)


def main(bq_client):
    st.title("Gym Locker Assignment Analysis")

    images_data = fetch_data_from_bigquery(bq_client)
    heatmap_data = generate_heatmap(images_data)
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, cmap="YlOrRd")
    plt.title("Locker Usage Heatmap")
    plt.xlabel("Locker Number")
    plt.ylabel("Row")
    st.pyplot(plt)


if __name__ == "__main__":
    main(bq_client)
