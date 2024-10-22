from google.cloud import bigquery
from google.oauth2 import service_account

# Assuming you're using service account credentials
SERVICE_ACCOUNT_FILE = "/Users/narcisfanica/Side-Projects/Gym Locker Keys/gcp_key.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Construct a BigQuery client object.
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# TODO(developer): Set dataset_id to the ID of the dataset to create.
dataset_id = "{}.gym_locker_data".format(client.project)

# Construct a full Dataset object to send to the API.
dataset = bigquery.Dataset(dataset_id)

# TODO(developer): Specify the geographic location where the dataset should reside.
dataset.location = "EU"

# Send the dataset to the API for creation, with an explicit timeout.
dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
print("Created dataset {}.{}".format(client.project, dataset.dataset_id))

# TODO(developer): Set table_id to the ID of the table to create.
table_id = "{}.{}.image_classification".format(client.project, dataset.dataset_id)

schema = [
    bigquery.SchemaField("image_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("locker_number", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("date_created", "STRING", mode="REQUIRED"),
    bigquery.SchemaField(
        "is_verified", "BOOLEAN", mode="REQUIRED", default_value_expression=False
    ),
    bigquery.SchemaField("author_name", "STRING", mode="NULLABLE"),
]

table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table)  # Make an API request.
print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))
