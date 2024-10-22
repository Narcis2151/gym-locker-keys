import os
from drive_helpers import download_file


def download_images(images):
    os.makedirs("../images", exist_ok=True)
    for photo in images:
        photo_id = photo["id"]
        photo_name = photo["name"]
        photo_path = os.path.join("../images", photo_name)

        download_file(photo_id, photo_path)
