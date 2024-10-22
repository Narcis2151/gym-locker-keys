import os
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from google.cloud import storage
from google.cloud import vision
from google.oauth2 import service_account

from download_images import download_images
from get_last_created_image import get_last_created_image
from classify_images import classify_images
from drive_helpers import list_folder, list_folder_with_dates

# Define the path to the service account key file
SERVICE_ACCOUNT_FILE = "/Users/narcisfanica/Side-Projects/Gym Locker Keys/gcp_key.json"

# Authenticate using service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Initialize BigQuery and GCS clients
bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

# Get the created date of the last image in the dataset
max_date_created = get_last_created_image(bq_client)
# Define Bucharest timezone
bucharest_tz = timezone(timedelta(hours=3))

# Ensure max_date_created is timezone-aware
if max_date_created.tzinfo is None:
    max_date_created = max_date_created.replace(tzinfo=bucharest_tz)
    max_date_created = max_date_created.astimezone(timezone.utc)

print(f"Last image created on: {max_date_created}")

# Get the list of folders in Google Drive
drive_folders = list_folder()

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
gym_locker_keys_photos = list_folder_with_dates(folder_id)
print("Number of photos in the folder:", len(gym_locker_keys_photos))

# Transform the images createdTime property to a datetime object
for photo in gym_locker_keys_photos:
    # Replace 'Z' with '+00:00' to make it ISO 8601 compliant
    photo["createdTime"] = photo["createdTime"].replace("Z", "+00:00")

    # Parse as timezone-aware datetime in UTC
    photo["createdTime"] = datetime.fromisoformat(photo["createdTime"])

    # Verify the parsed time
    print("Photo's Created Time (UTC):", photo["createdTime"])

# Filter the list of folders and files to only include those created after the last image in the dataset
if max_date_created is not None:
    new_gym_locker_keys_photos = [
        photo
        for photo in gym_locker_keys_photos
        if photo["createdTime"] > max_date_created
    ]
else:
    new_gym_locker_keys_photos = gym_locker_keys_photos

print("Number of new photos:", len(new_gym_locker_keys_photos))

if len(new_gym_locker_keys_photos) == 0:
    print("No new photos to process.")
    exit()

# Download the new photos to the local filesystem
download_images(new_gym_locker_keys_photos)

# Define the bucket name
bucket_name = "gym-locker-keys_images"

# Get the bucket
bucket = storage_client.get_bucket(bucket_name)

# Upload the new photos to the bucket
for photo in new_gym_locker_keys_photos:
    photo_path = f"../images/{photo['name']}"
    blob = bucket.blob(f"unverified_images/{photo["name"]}")
    blob.upload_from_filename(photo_path)

print(f"Uploaded {len(new_gym_locker_keys_photos)} photos to the bucket.")

# Delete the photos from the local filesystem
os.system("rm -rf ../images/*")
os.system("rm -rf ../images")


# Classify the new photos using the Vision API
rows_to_insert = classify_images(vision_client, storage_client, bucket_name, images=new_gym_locker_keys_photos)
print("Number of classified images:", len(rows_to_insert))
print(rows_to_insert)

# Insert the classified images into BigQuery
errors = bq_client.insert_rows_json(
    "gym-locker-keys.gym_locker_data.image_classification",
    rows_to_insert,
)

if errors == []:
    print("Rows successfully inserted into BigQuery.")
else:
    print("Errors occurred while inserting rows into BigQuery.")
    print(errors)
