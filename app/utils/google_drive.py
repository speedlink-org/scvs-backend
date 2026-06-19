# import os
# import io
# import pickle
# import tempfile
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload

# class GoogleDriveService:
#     def __init__(self):
#         self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
#         self.creds = None
#         self.service = None
#         self.folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
#         self._authenticate()
        
#     def _authenticate(self):
#         """Authenticate using OAuth 2.0 - loads existing token or creates new one"""
#         token_path = os.path.join(tempfile.gettempdir(), 'drive_token.pickle')
        
#         print("Initializing Google Drive...")
        
#         # Try to load existing token
#         if os.path.exists(token_path):
#             try:
#                 with open(token_path, 'rb') as token:
#                     self.creds = pickle.load(token)
#                 print("Loaded existing credentials")
#             except:
#                 print("Could not load existing credentials")
        
#         # If no valid credentials, we need to get new ones
#         if not self.creds or not self.creds.valid:
#             if self.creds and self.creds.expired and self.creds.refresh_token:
#                 print("Refreshing expired credentials...")
#                 self.creds.refresh(Request())
#             else:
#                 print("No valid credentials. You need to run the setup script.")
#                 print("Run: python setup_google_drive.py")
#                 return
            
#             # Save refreshed credentials
#             with open(token_path, 'wb') as token:
#                 pickle.dump(self.creds, token)
        
#         # Build the service
#         self.service = build('drive', 'v3', credentials=self.creds)
#         print(f"Google Drive authenticated successfully")
#         print(f"Using folder ID: {self.folder_id}")
    
#     def is_authenticated(self):
#         """Check if we're authenticated"""
#         return self.service is not None
    
#     def upload_file(self, file_bytes, filename, mime_type='image/png'):
#         """Upload file to Google Drive"""
#         if not self.service:
#             print("Not authenticated. Run setup script first.")
#             return self._save_temp(file_bytes, filename)
        
#         if not self.folder_id:
#             print("GOOGLE_DRIVE_FOLDER_ID not set")
#             return self._save_temp(file_bytes, filename)
        
#         try:
#             print(f"Uploading {filename}...")
            
#             file_metadata = {
#                 'name': filename,
#                 'parents': [self.folder_id]
#             }
            
#             file_obj = io.BytesIO(file_bytes)
#             media = MediaIoBaseUpload(file_obj, mimetype=mime_type)
            
#             # Upload file
#             file = self.service.files().create(
#                 body=file_metadata,
#                 media_body=media,
#                 fields='id, name'
#             ).execute()
            
#             file_id = file.get('id')
#             print(f"File uploaded, ID: {file_id}")
            
#             # Make file publicly readable
#             self.service.permissions().create(
#                 fileId=file_id,
#                 body={
#                     'type': 'anyone',
#                     'role': 'reader',
#                     'allowFileDiscovery': False
#                 }
#             ).execute()
            
#             # Return direct view link
#             url = f"https://drive.google.com/uc?export=view&id={file_id}"
#             print(f"Public URL: {url}")
#             return url
            
#         except Exception as error:
#             print(f"Upload failed: {error}")
#             return self._save_temp(file_bytes, filename)
    
#     def _save_temp(self, file_bytes, filename):
#         """Fallback: save to temporary directory"""
#         try:
#             temp_dir = '/tmp/qrcodes'
#             os.makedirs(temp_dir, exist_ok=True)
#             temp_path = os.path.join(temp_dir, filename)
            
#             with open(temp_path, 'wb') as f:
#                 f.write(file_bytes)
            
#             print(f"Saved to temporary location: {temp_path}")
#             return temp_path
#         except Exception as e:
#             print(f"Failed to save locally: {e}")
#             return None

# # Global instance
# drive_service = GoogleDriveService()