import os
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

class GoogleDriveService:
    def __init__(self):
        self.folder_id = os.getenv("DRIVE_FOLDER_ID")

        service_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

        if not service_file or not os.path.exists(service_file):
            print(" Service account JSON file missing")
            self.service = None
            return

        scopes = ["https://www.googleapis.com/auth/drive"]

        creds = Credentials.from_service_account_file(
            service_file,
            scopes=scopes
        )

        self.service = build("drive", "v3", credentials=creds)
        print("Google Drive authenticated using Service Account")

    def upload_file(self, file_bytes, filename, mime_type="image/png"):
        if not self.service:
            print(" Drive service not initialized")
            return None
        
        file_metadata = {
            "name": filename,
            "parents": [self.folder_id]
        }

        file_stream = io.BytesIO(file_bytes)
        media = MediaIoBaseUpload(file_stream, mimetype=mime_type)

        # Upload file
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get("id")

        # Make file public
        self.service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        public_url = f"https://drive.google.com/uc?export=view&id={file_id}"

        return public_url

drive_service = GoogleDriveService()

