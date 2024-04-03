import os
import sqlite3
import pickle
import requests
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import mimetypes
import time

def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create or modify tables as necessary
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS albums (
            id TEXT PRIMARY KEY,
            title TEXT,
            productUrl TEXT,
            mediaItemsCount INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id TEXT PRIMARY KEY,
            albumId TEXT,
            albumName TEXT,
            filename TEXT,
            mimeType TEXT,
            productUrl TEXT,
            baseUrl TEXT,
            creationDate TIMESTAMP,
            FOREIGN KEY (albumId) REFERENCES albums (id)
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_store_all_media_items(service, db_path):
    page_token = None
    while True:
        try:
            response = service.mediaItems().list(pageSize=100, pageToken=page_token).execute()
            for item in response.get('mediaItems', []):
                photo_id = item['id']
                if not item_already_exists(db_path, 'photos', photo_id):
                    media_metadata = item.get('mediaMetadata', {})
                    creation_date = media_metadata.get('creationTime', 'Unknown')

                    photo_data = {
                        'id': photo_id,
                        'filename': item.get('filename', 'Unknown'),
                        'baseUrl': item['baseUrl'],
                        'productUrl' : item['productUrl'],
                        'mimeType': item.get('mimeType', 'Unknown'),
                        'creationDate': creation_date,
                    }
                    add_item_to_db(db_path, photo_data)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f"An error occurred while fetching media items: {error}")
            break


# Check if an album or photo already exists in the DB
def item_already_exists(db_path, table_name, item_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Add album or photo to the DB
def add_item_to_db(db_path, photo_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the photo already exists
    cursor.execute("SELECT id FROM photos WHERE id = ?", (photo_data['id'],))
    exists = cursor.fetchone()

    if exists:
        # Update the existing record with potential new album info
        cursor.execute("""
            UPDATE photos 
            SET albumId = ?, albumName = ?, 
                filename = ?, productUrl = ?, baseUrl = ?, mimeType = ?, 
                creationDate = ?
            WHERE id = ?""", 
            (photo_data.get('albumId'), photo_data.get('albumName'), 
             photo_data['filename'], photo_data['productUrl'],photo_data['baseUrl'], 
             photo_data['mimeType'], photo_data['creationDate'], 
             photo_data['id']))
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO photos (id, albumId, albumName, filename, productUrl, baseUrl, mimeType, 
                                creationDate) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
            (photo_data['id'], photo_data.get('albumId'), photo_data.get('albumName'), 
            photo_data['filename'], photo_data['productUrl'], photo_data['baseUrl'], 
            photo_data['mimeType'], photo_data['creationDate']))



    conn.commit()
    conn.close()

def fetch_and_store_photos_for_album(service, db_path, album_id, album_name):
    page_token = None
    while True:
        try:
            response = service.mediaItems().search(body={'albumId': album_id, 'pageToken': page_token}).execute()
            for item in response.get('mediaItems', []):
                photo_id = item['id']
                if not item_already_exists(db_path, 'photos', photo_id):
                    media_metadata = item.get('mediaMetadata', {})
                    creation_date = media_metadata.get('creationTime', 'Unknown')

                    photo_data = {
                        'id': photo_id,
                        'albumId': album_id,  # Include album ID
                        'albumName': album_name,  # Include album name
                        'filename': item.get('filename', 'Unknown'),
                        'productUrl' : item['productUrl'],
                        'baseUrl': item['baseUrl'],
                        'mimeType': item.get('mimeType', 'Unknown'),
                        'creationDate': creation_date,
                    }
                    add_item_to_db(db_path, photo_data)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f"An error occurred while fetching photos for album {album_id}: {error}")
            break

def update_photo_album_info(db_path, photo_id, album_id, album_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE photos SET albumId = ?, albumName = ? WHERE id = ?", (album_id, album_name, photo_id))
    conn.commit()
    conn.close()

def fetch_and_store_photos(service, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM albums")
    albums = cursor.fetchall()
    conn.close()

    for album_id, album_name in albums:
        fetch_and_store_photos_for_album(service, db_path, album_id, album_name)

def fetch_and_store_albums(service, db_path):
    page_token = None
    while True:
        try:
            response = service.albums().list(pageSize=50, pageToken=page_token, fields="nextPageToken,albums(id,title,productUrl,mediaItemsCount)").execute()
            for album in response.get('albums', []):
                album_id = album['id']
                if not item_already_exists(db_path, 'albums', album_id):
                    album_data = {
                        'id': album_id,
                        'title': album['title'],
                        'productUrl': album['productUrl'],
                        'mediaItemsCount': album.get('mediaItemsCount', 0),
                    }
                    add_album_to_db(db_path, album_data)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f"An error occurred while fetching albums: {error}")
            break

def add_album_to_db(db_path, album_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO albums (id, title, productUrl, mediaItemsCount) 
        VALUES (?, ?, ?, ?)""", 
        (album_data['id'], album_data['title'], album_data['productUrl'], 
         album_data['mediaItemsCount']))

    conn.commit()
    conn.close()


def fetch_and_store_photos_for_album(service, db_path, album_id, album_name):
    page_token = None
    while True:
        try:
            response = service.mediaItems().search(body={'albumId': album_id, 'pageToken': page_token}).execute()
            for item in response.get('mediaItems', []):
                photo_id = item['id']
                if not item_already_exists(db_path, 'photos', photo_id):
                    media_metadata = item.get('mediaMetadata', {})
                    creation_date = media_metadata.get('creationTime', 'Unknown')

                    photo_data = {
                        'id': photo_id,
                        'albumId': album_id,
                        'albumName': album_name,
                        'filename': item.get('filename', 'Unknown'),
                        'productUrl' : item['productUrl'],
                        'baseUrl': item['baseUrl'],
                        'mimeType': item.get('mimeType', 'Unknown'),
                        'creationDate': creation_date,
                    }
                    add_item_to_db(db_path, photo_data)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        except HttpError as error:
            print(f"An error occurred while fetching photos for album {album_id}: {error}")
            break

# Updated Google Photos API functions
def create_service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    cred = None
    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=cred, static_discovery=False), cred

def update_photo_album_names(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE photos
        SET albumName = (
            SELECT title FROM albums WHERE albums.id = photos.albumId
        )
    ''')
    conn.commit()
    conn.close()

def main():
    db_path = 'database.db'
    client_secret_file = 'client_secrets.json'
    api_name = 'photoslibrary'
    api_version = 'v1'
    scopes = ['https://www.googleapis.com/auth/photoslibrary']

    # Initialize the database
    initialize_db(db_path)

    # Create the Google Photos service instance
    service, _ = create_service(client_secret_file, api_name, api_version, scopes)

    # Fetch and store album data
    fetch_and_store_albums(service, db_path)

    # Fetch and store photos for each album (updating the album information for each photo)
    fetch_and_store_photos(service, db_path)

    # Fetch and store all media items data
    fetch_and_store_all_media_items(service, db_path)

if __name__ == '__main__':
    main()
