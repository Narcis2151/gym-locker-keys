import io
import os
import pandas as pd
from google.oauth2 import service_account
from google.cloud import vision

# Define the Google Drive API scopes and service account file path
SERVICE_ACCOUNT_FILE = "/Users/narcisfanica/Side-Projects/Gym Locker Keys/gcp_key.json"

# Create credentials using the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE
)

# Create a Google Cloud Vision client using the credentials
client = vision.ImageAnnotatorClient(credentials=credentials)

# Define the path to the image file
folder_path = "/Users/narcisfanica/Side-Projects/Gym Locker Keys/images"

# Create a pandas dataframe with 2 columns, one for the image path and one for the text
df = pd.DataFrame(columns=["image_path", "text"])

for image_path in os.listdir(folder_path):
    # Read the image file
    with io.open(os.path.join(folder_path, image_path), "rb") as image_file:
        content = image_file.read()
        image = vision.Image(content=content)

        # Perform text detection on the image
        response = client.text_detection(image=image)
        texts = response.text_annotations

        # For every text, if the text contains exactly 3 digits and the previous text is a "#" character, append it to the dataframe
        for index, text in enumerate(texts):
            if (
                text.description.isdigit()
                and len(text.description) == 3
                and texts[index - 1].description == "#"
            ):
                df = df._append(
                    {
                        "image_path": image_path,
                        "text": text.description,
                    },
                    ignore_index=True,
                )


# Save the dataframe to a CSV file
df.to_csv("image_text.csv", index=False)

