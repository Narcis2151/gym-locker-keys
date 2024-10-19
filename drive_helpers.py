import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Define the Google Drive API scopes and service account file path
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "/Users/narcisfanica/Side-Projects/Gym Locker Keys/gcp_key.json"

# Create credentials using the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Google Drive service
drive_service = build("drive", "v3", credentials=credentials)


def create_folder(folder_name, parent_folder_id=None):
    """Create a folder in Google Drive and return its ID."""
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_folder_id] if parent_folder_id else [],
    }

    created_folder = (
        drive_service.files().create(body=folder_metadata, fields="id").execute()
    )

    print(f'Created Folder ID: {created_folder["id"]}')
    return created_folder["id"]


def list_folder(parent_folder_id=None):
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
        print("No folders or files found in Google Drive.")
        return []
    else:
        print("Folders and files in Google Drive:")
        for item in items:
            print(f'{item["name"]} ({item["mimeType"]}) - ID: {item["id"]}')
        return items


def delete_files(file_or_folder_id):
    """Delete a file or folder in Google Drive by ID."""
    try:
        drive_service.files().delete(fileId=file_or_folder_id).execute()
        print(f"Successfully deleted file/folder with ID: {file_or_folder_id}")
    except Exception as e:
        print(f"Error deleting file/folder with ID: {file_or_folder_id}")
        print(f"Error details: {str(e)}")


def download_file(file_id, destination_path):
    """Download a file from Google Drive by its ID."""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, mode="wb")

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

