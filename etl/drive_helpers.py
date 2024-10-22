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
        return []
    else:
        return items


def list_folder_with_dates(parent_folder_id=None):
    if parent_folder_id:
        query = f"'{parent_folder_id}' in parents and trashed=false and mimeType contains 'image/'"
    else:
        query = "'me' in owners or sharedWithMe and trashed=false and mimeType contains 'image/'"

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


def download_file(file_id, destination_path):
    """Download a file from Google Drive by its ID."""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, mode="wb")

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        # print(f"Download {int(status.progress() * 100)}%.")
