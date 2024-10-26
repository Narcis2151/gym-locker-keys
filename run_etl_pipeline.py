from google.cloud import bigquery
from google.cloud import storage
from google.cloud import vision
from googleapiclient.discovery import build

from etl_functions import (
    get_last_created_image,
    insert_into_bigquery,
    list_folder,
    list_files_from_folder,
    classify_images,
    transfer_file,
)

# Initialize BigQuery and GCS clients
bq_client = bigquery.Client()
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
drive_service = build("drive", "v3")

# Get the created date of the last image in the dataset
max_date_created = get_last_created_image(bq_client)
print(f"Last image in database created on: {max_date_created}")

# Get the list of folders in Google Drive
drive_folders = list_folder(drive_service)

# Find the folder ID of the "Gym Locker Keys" folder
folder_id = None
for folder in drive_folders:
    if folder["name"] == "Gym Locker Keys":
        folder_id = folder["id"]
        break

# Exit the script if the "Gym Locker Keys" folder is not found
if folder_id is None:
    print("Folder not found in Google Drive.")
    exit()

# List the folders and files in the "Gym Locker Keys" folder
gym_locker_keys_photos = list_files_from_folder(
    drive_service, folder_id, max_date_created
)
print("Number of photos found in the folder:", len(gym_locker_keys_photos))

if len(gym_locker_keys_photos) == 0:
    print("No new photos to process.")
    exit()

# Define the bucket name
bucket_name = "gym-locker-keys_images"

# Get the bucket
bucket = storage_client.get_bucket(bucket_name)

blobs = []
# Upload the new photos to the bucket
for photo in gym_locker_keys_photos:
    blob = transfer_file(
        drive_service, storage_client, photo["id"], bucket_name, photo["name"]
    )
    blobs.append({"name": blob.name, "createdTime": photo["createdTime"]})

print(f"Uploaded {len(gym_locker_keys_photos)} photos to the bucket.")


# Classify the new photos using the Vision API
rows_to_insert = classify_images(vision_client, bucket_name, blobs)
print("Number of classified images:", len(rows_to_insert))

# Insert the classified images into BigQuery
insert_into_bigquery(bq_client, rows_to_insert)
