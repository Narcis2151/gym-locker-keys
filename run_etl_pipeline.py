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

# Get the created date of the last image in the dataset for each gym
max_date_created_700_fit = get_last_created_image(bq_client, '700_fit')
max_date_created_sweat = get_last_created_image(bq_client, 'sweat')

print(f"Last image in the database for 700 Fit created on: {max_date_created_700_fit}")
print(f"Last image in the database for Sweat created on: {max_date_created_sweat}")

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

subfolders = list_folder(drive_service, folder_id)

# Find the folder ID of the "700 Fit" folder
folder_id_700_fit = None
for folder in subfolders:
    if folder["name"] == "700 Fit":
        folder_id_700_fit = folder["id"]
        break

# Exit the script if the "700 Fit" folder is not found
if folder_id_700_fit is None:
    print("Folder not found in Google Drive.")
    exit()

# Find the folder ID of the "Sweat" folder
folder_id_sweat = None
for folder in subfolders:
    if folder["name"] == "Sweat":
        folder_id_sweat = folder["id"]
        break

# Exit the script if the "Sweat" folder is not found
if folder_id_sweat is None:
    print("Folder not found in Google Drive.")
    exit()

# List the folders and files in the subfolders
photos_700_fit = list_files_from_folder(
    drive_service, folder_id_700_fit, max_date_created_700_fit
)
photos_sweat = list_files_from_folder(
    drive_service, folder_id_sweat, max_date_created_sweat
)

print("Number of photos found for 700 Fit:", len(photos_700_fit))
print("Number of photos found for Sweat:", len(photos_sweat))

photos_700_fit = [
    {
        'id': photo['id'],
        'name': photo['name'],
        'createdTime': photo['createdTime'],
        'gym': '700_fit'
    } for photo in photos_700_fit]

photos_sweat = [
    {
        'id': photo['id'],
        'name': photo['name'],
        'createdTime': photo['createdTime'],
        'gym': 'sweat'
    } for photo in photos_sweat]

all_photos = photos_700_fit + photos_sweat

if len(all_photos) == 0:
    print("No new photos to process.")
    exit()

# Define the bucket name
bucket_name = "gym-locker-keys_images"

# Get the bucket
bucket = storage_client.get_bucket(bucket_name)

blobs = []
# Upload the new photos to the bucket
for photo in all_photos:
    blob = transfer_file(
        drive_service, storage_client, photo["id"], bucket_name, photo["name"], photo['gym']
    )
    blobs.append({"name": blob.name, "createdTime": photo["createdTime"], "gym": photo['gym']})

print(f"Uploaded {len(all_photos)} photos to the bucket.")

# Classify the new photos using the Vision API
rows_to_insert = classify_images(vision_client, bucket_name, blobs)
print("Number of classified images:", len(rows_to_insert))

# Insert the classified images into BigQuery
insert_into_bigquery(bq_client, rows_to_insert)
