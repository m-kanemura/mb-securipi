""" credit --- https://www.youtube.com/watch?v=tamT_iGoZDQ """

from googleapiclient.discovery import build
from google.oauth2 import service_account

import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Define email sender and receiver
email_sender = os.environ.get('EMAIL_SENDER')

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
PARENT_FOLDER_ID = os.environ.get('PARENT_FOLDER_ID')

def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_video(file_path, file_name):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name' : file_name,
        'parents' : [PARENT_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=file_path + file_name
    ).execute()

    print("upload to google drive complete!")