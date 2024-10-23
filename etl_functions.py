from io import BytesIO
from google.cloud import vision
from googleapiclient.http import MediaIoBaseDownload


def list_folder(drive_service, parent_folder_id=None):
    """List folders and files in Google Drive."""
    if parent_folder_id:
        query = f"'{parent_folder_id}' in parents and trashed=false"
    else:
        query = "'me' in owners or sharedWithMe and trashed=false"

    results = (
        drive_service.files()
        .list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType)",
        )
        .execute()
    )
    items = results.get("files", [])

    if not items:
        return []
    else:
        return items


def list_files_from_folder(drive_service, parent_folder_id=None, start_date=None):
    if parent_folder_id:
        query = f"'{parent_folder_id}' in parents"
    else:
        query = "'me' in owners or sharedWithMe"
    query = f"{query} and trashed=false"
    query = f"{query} and mimeType contains 'image/'"
    if start_date:
        query = f"{query} and createdTime > '{start_date.isoformat()}'"

    results = (
        drive_service.files()
        .list(
            q=query,
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, createdTime)",
        )
        .execute()
    )
    items = results.get("files", [])

    return items


def get_last_created_image(bq_client):
    query = """
    SELECT max(datetime(timestamp(date_created))) as latest_date
    FROM `gym-locker-keys.gym_locker_data.image_classification`
    """
    query_job = bq_client.query(query)
    results = query_job.result()
    for row in results:
        return row.latest_date
    return None  # If table is empty


def transfer_file(
    drive_service, storage_client, file_id, bucket_name, destination_blob_name
):
    # Download file from Google Drive to in-memory buffer
    request = drive_service.files().get_media(fileId=file_id)
    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        # print(f"Download {int(status.progress() * 100)}%.")

    # Reset buffer position to start
    fh.seek(0)

    # Upload the file to Cloud Storage
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f"unverified_images/{destination_blob_name}")
    blob.upload_from_file(fh)

    print("File transferred to Cloud Storage.")
    return blob


def classify_images(vision_client, bucket_name, blobs):
    rows_to_insert = []

    for blob in blobs:
        image_uri = f"gs://{bucket_name}/{blob["name"]}"
        image = vision.Image(source=vision.ImageSource(gcs_image_uri=image_uri))

        # Perform text detection
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations

        # Extract locker number
        locker_number = None
        for index, text in enumerate(texts):
            if (
                text.description.isdigit()
                and len(text.description) == 3
                and texts[index - 1].description == "#"
            ):
                locker_number = int(text.description)
                break

        if locker_number:
            rows_to_insert.append(
                {
                    "blob_name": blob["name"],
                    "image_name": f"unverified_{locker_number}",
                    "locker_number": locker_number,
                    "date_created": str(blob["createdTime"]),
                    "is_verified": False,
                }
            )

    return rows_to_insert


def insert_into_bigquery(bq_client, rows_to_insert):
    if len(rows_to_insert) == 0:
        print("No images to insert into BigQuery.")
        exit()

    errors = bq_client.insert_rows_json(
        "gym-locker-keys.gym_locker_data.image_classification",
        rows_to_insert,
    )

    if errors == []:
        print("Rows successfully inserted into BigQuery.")
    else:
        print("Errors occurred while inserting rows into BigQuery.")
        print(errors)
