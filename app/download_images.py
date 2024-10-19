import os
import io
from drive_helpers import list_folder, download_file

# Get the list of folders in Google Drive
drive_folders = list_folder()

# Find the folder ID of the "Gym Locker Keys" folder
gym_locker_keys_folder_id = None
for folder in drive_folders:
    if folder["name"] == "Gym Locker Keys":
        gym_locker_keys_folder_id = folder["id"]
        break

# Exit the script if the "Gym Locker Keys" folder is not found
if gym_locker_keys_folder_id is None:
    print("Gym Locker Keys folder not found in Google Drive.")
    exit()

# List the folders and files in the "Gym Locker Keys" folder
gym_locker_keys_photos = list_folder(gym_locker_keys_folder_id)

# Create a folder in the root dir of the project named "images"
os.makedirs("images", exist_ok=True)

# Download images from the "Gym Locker Keys" folder
for photo in gym_locker_keys_photos:
    photo_id = photo["id"]
    photo_name = photo["name"]
    photo_path = os.path.join("images", photo_name)

    download_file(photo_id, photo_path)
