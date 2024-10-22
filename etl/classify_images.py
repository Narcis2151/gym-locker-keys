from google.cloud import vision
from datetime import datetime


def classify_images(vision_client, storage_client, bucket_name, images):
    bucket = storage_client.get_bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix="unverified_images/"))
    blobs = [blob for blob in blobs if f"unverified_images/{blob.name}" in images]
    print("Number of blobs in the bucket:", len(blobs))
    rows_to_insert = []

    for blob in blobs:
        print(blob.name)
        image_uri = f"gs://{bucket_name}/{blob.name}"
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
                    "image_name": f"unverified_{locker_number}",
                    "locker_number": locker_number,
                    "date_created": str(datetime.now()),
                    "is_verified": False,
                }
            )

    return rows_to_insert
