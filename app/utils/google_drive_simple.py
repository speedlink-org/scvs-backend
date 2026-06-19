# utils/google_drive.py
import os
import io
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError

class GoogleDriveService:
    def __init__(self):
        # Get service account info from environment variables
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
        }
        
        print("Initializing Google Drive Service for Shared Drive...")
        print(f"Service Account: {service_account_info['client_email']}")
        
        # Create credentials
        self.creds = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build the service
        self.service = build('drive', 'v3', credentials=self.creds)
        
        # Get Shared Drive ID from environment
        self.drive_id = os.getenv('GOOGLE_SHARED_DRIVE_ID')  # The SHARED DRIVE ID
        self.folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')  # Folder WITHIN the shared drive
        
        print(f"Shared Drive ID: {self.drive_id}")
        print(f"Folder ID: {self.folder_id}")
        
        if not self.drive_id:
            print("WARNING: GOOGLE_SHARED_DRIVE_ID not set")
        if not self.folder_id:
            print("WARNING: GOOGLE_DRIVE_FOLDER_ID not set")
        
        print("Google Drive service initialized")
    
    def upload_file(self, file_bytes, filename, mime_type='image/png'):
        """Upload file to Shared Drive"""
        try:
            if not self.folder_id:
                raise Exception("GOOGLE_DRIVE_FOLDER_ID not set")
            
            print(f"Uploading {filename} to Shared Drive...")
            
            # File metadata
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            # Create media upload
            file_obj = io.BytesIO(file_bytes)
            media = MediaIoBaseUpload(file_obj, mimetype=mime_type, resumable=True)
            
            # Upload parameters for Shared Drive
            upload_params = {
                'body': file_metadata,
                'media_body': media,
                'fields': 'id, name, webViewLink',
                'supportsAllDrives': True  # CRITICAL for Shared Drives
            }
            
            # If we have a Shared Drive ID, use it
            if self.drive_id:
                upload_params['driveId'] = self.drive_id
                upload_params['supportsAllDrives'] = True
            
            # Upload the file
            file = self.service.files().create(**upload_params).execute()
            
            file_id = file.get('id')
            print(f"File uploaded, ID: {file_id}")
            
            # Make file publicly readable
            try:
                self.service.permissions().create(
                    fileId=file_id,
                    body={
                        'type': 'anyone',
                        'role': 'reader',
                        'allowFileDiscovery': False
                    },
                    supportsAllDrives=True
                ).execute()
                print("File made publicly accessible")
            except Exception as perm_error:
                print(f"Could not set public permissions: {perm_error}")
            
            # Return direct view link
            url = f"https://drive.google.com/uc?export=view&id={file_id}"
            print(f"Public URL: {url}")
            return url
            
        except HttpError as error:
            print(f"Google Drive API Error: {error}")
            if error.resp.status == 404:
                print("   Error 404: Folder not found or no access")
                print(f"   Check if service account has access to folder: {self.folder_id}")
            elif error.resp.status == 403:
                print("   Error 403: Permission denied")
                print("   Service account needs 'Content Manager' or 'Editor' role in Shared Drive")
            return self._save_temp_fallback(file_bytes, filename)
            
        except Exception as error:
            print(f"Upload Error: {error}")
            return self._save_temp_fallback(file_bytes, filename)
    
    def _save_temp_fallback(self, file_bytes, filename):
        """Fallback to save file temporarily"""
        try:
            temp_dir = '/tmp/qrcodes'
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)
            
            print(f"Saved to temporary location: {temp_path}")
            return temp_path
        except Exception as e:
            print(f"Failed to save locally: {e}")
            return None
    
    def delete_file(self, file_url):
        """Delete a file from Google Drive using its URL"""
        try:
            # Extract file ID from URL
            if 'id=' in file_url:
                file_id = file_url.split('id=')[1].split('&')[0]
                
                print(f"Deleting file: {file_id}")
                self.service.files().delete(
                    fileId=file_id,
                    supportsAllDrives=True
                ).execute()
                
                print(f"File deleted successfully")
                return True
                
        except Exception as error:
            print(f"Error deleting file: {error}")
        
        return False

# Global instance
drive_service = GoogleDriveService()
