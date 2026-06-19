# # utils/google_drive_oauth.py
# import os
# import io
# import pickle
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload
# import tempfile

# class GoogleDriveOAuthService:
#     def __init__(self):
#         self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
#         self.creds = None
#         self.service = None
#         self.folder_id = None
#         self._authenticate()
        
#     def _authenticate(self):
#         """Authenticate using OAuth 2.0"""
#         token_path = os.path.join(tempfile.gettempdir(), 'drive_token.pickle')
        
#         # Try to load existing token
#         if os.path.exists(token_path):
#             with open(token_path, 'rb') as token:
#                 self.creds = pickle.load(token)
        
#         # If no valid credentials, get new ones
#         if not self.creds or not self.creds.valid:
#             if self.creds and self.creds.expired and self.creds.refresh_token:
#                 self.creds.refresh(Request())
#             else:
#                 # Create flow from client config
#                 flow = InstalledAppFlow.from_client_config(
#                     {
#                         "installed": {
#                             "client_id": os.getenv('GOOGLE_CLIENT_ID', '1936528-nspdgsobqd87.apps.googleusercontent.com'),
#                             "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', 'GOCSPX-xjLHYHFkq'),
#                             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                             "token_uri": "https://oauth2.googleapis.com/token",
#                             "redirect_uris": ["http://localhost:8080/"]
#                         }
#                     },
#                     scopes=self.SCOPES
#                 )
                
#                 # Run local server for authentication
#                 self.creds = flow.run_local_server(port=8080)
            
#             # Save credentials for next run
#             with open(token_path, 'wb') as token:
#                 pickle.dump(self.creds, token)
        
#         self.service = build('drive', 'v3', credentials=self.creds)
        
#         # Get folder ID from environment
#         self.folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        
#         print(f"Google Drive authenticated as: {self.creds.client_id}")
#         print(f"Using folder ID: {self.folder_id}")
    
#     def upload_file(self, file_bytes, filename, mime_type='image/png'):
#         """Upload file to Google Drive"""
#         if not self.folder_id:
#             raise Exception("GOOGLE_DRIVE_FOLDER_ID not set")
        
#         try:
#             file_metadata = {
#                 'name': filename,
#                 'parents': [self.folder_id]
#             }
            
#             file_obj = io.BytesIO(file_bytes)
#             media = MediaIoBaseUpload(file_obj, mimetype=mime_type, resumable=True)
            
#             # Upload file
#             file = self.service.files().create(
#                 body=file_metadata,
#                 media_body=media,
#                 fields='id, name, webViewLink'
#             ).execute()
            
#             print(f"File uploaded: {filename}")
            
#             # Make file publicly readable
#             self.service.permissions().create(
#                 fileId=file['id'],
#                 body={'type': 'anyone', 'role': 'reader'}
#             ).execute()
            
#             # Return viewable URL
#             return f"https://drive.google.com/uc?export=view&id={file['id']}"
            
#         except Exception as e:
#             print(f"Upload error: {e}")
#             # Fallback
#             return self._save_temp_fallback(file_bytes, filename)
    
#     def _save_temp_fallback(self, file_bytes, filename):
#         """Fallback to temp storage"""
#         temp_dir = '/tmp/qrcodes'
#         os.makedirs(temp_dir, exist_ok=True)
#         temp_path = os.path.join(temp_dir, filename)
        
#         with open(temp_path, 'wb') as f:
#             f.write(file_bytes)
        
#         print(f"Saved locally: {temp_path}")
#         return temp_path

# # Global instance
# drive_service = GoogleDriveOAuthService()