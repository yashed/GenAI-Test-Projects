import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
import time

# Setup Google API credentials
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def list_files(service, folder_id):
    """List files and subfolders in Google Drive within a specific folder."""
    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query, spaces='drive',
        fields="nextPageToken, files(id, name, mimeType, modifiedTime)").execute()
    return results.get('files', [])

def fetch_file_content(service, file_id, mime_type):
    """Fetch content from Google Docs or Slides."""
    if mime_type == "application/vnd.google-apps.document":
        document = service.files().export(fileId=file_id, mimeType='text/plain').execute()
        return document.decode('utf-8')
    elif mime_type == "application/vnd.google-apps.presentation":
        slides = service.files().export(fileId=file_id, mimeType='text/plain').execute()
        return slides.decode('utf-8')
    return None

def process_and_store_content(contents, vector_db, file_name):
    """Embed and store document data in vector database."""
    embeddings = OpenAIEmbeddings()
    texts = [contents]
    metadatas = [{"source": file_name}]
    vector_db.add_texts(texts, metadatas)
    vector_db.persist()  # Save to disk

def track_changes_recursive(service, folder_id, vector_db):
    """Recursively track changes and update vector DB if any changes occur."""
    files = list_files(service, folder_id)
    for file in files:
        print(f"Checking file: {file['name']}")

        if file['mimeType'] == "application/vnd.google-apps.folder":
            # If the file is a folder, recursively call this function
            print(f"Entering folder: {file['name']}")
            track_changes_recursive(service, file['id'], vector_db)
        else:
            # Process documents
            last_modified_time = file['modifiedTime']
            print(f"Last modified: {last_modified_time}")

            content = fetch_file_content(service, file['id'], file['mimeType'])
            if content:
                process_and_store_content(content, vector_db, file['name'])
                print(f"Stored or updated embeddings for {file['name']}")
            else:
                print(f"No content found for {file['name']}")

def main():
    # Authenticate with Google Drive
    service = authenticate_google_drive()

    # Specify the folder ID for the root folder
    folder_id = '1NsT2UvFfjrCCBnPdYG4D1WZPgJdgmyly'

    # Ensure the VectorDB directory exists
    vector_db_path = os.path.join(os.getcwd(), "VectorDB")
    os.makedirs(vector_db_path, exist_ok=True)

    # Initialize Chroma vector database
    vector_db = Chroma(
        "google_drive_docs",
        embedding_function=OpenAIEmbeddings(),
        persist_directory=vector_db_path
    )

    # Initial run to fetch and store content recursively
    track_changes_recursive(service, folder_id, vector_db)

    # Setup a loop to periodically check for updates
    while True:
        print("Checking for updates...")
        track_changes_recursive(service, folder_id, vector_db)
        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    main()
