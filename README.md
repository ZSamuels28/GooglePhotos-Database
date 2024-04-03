# GooglePhotos-Database

This Python application is designed to synchronize your Google Photos albums and media items with a local SQLite database. By fetching albums and photos from your Google Photos account, it creates a comprehensive, searchable local copy of your media library. This tool is especially useful for backing up photo metadata or managing photo albums/photos.

## Features

- Synchronize Google Photos albums and media items with a local SQLite database.
- Store detailed information about each photo, including album associations, file names, mime types, and creation dates.
- Automatically handle pagination to fetch all available data from Google Photos.
- Update local database records to reflect changes in album names or photo details.

## Prerequisites

- Python 3.x
- Google account with Google Photos enabled
- `google-auth-oauthlib` and `google-api-python-client` Python libraries

## Setup

### Step 1: Clone the Repository

Clone this repository to your local machine using `git` or download the ZIP package directly.

```bash
git clone https://yourrepositorylink.git
cd google-photos-db-sync
```

### Step 2: Install Dependencies

Install the required Python libraries by running: `pip install -r requirements.txt`

### Step 3: Create a Google Cloud Project and Enable the Google Photos API
1. Go to the Google Cloud Console.
2. Create a new project.
3. Navigate to the "APIs & Services > Dashboard" section.
4. Click "+ ENABLE APIS AND SERVICES" and search for "Google Photos Library API".
5. Enable the "Google Photos Library API" for your project.

### Step 4: Create Credentials
1. In the Google Cloud Console, go to "APIs & Services > Credentials".
2. Click "Create credentials" and select "OAuth client ID".
3. Choose "Desktop app" as the application type.
4. Enter a name for your OAuth 2.0 client and click "Create".
5. Download the JSON file containing your client credentials.

### Step 5: Configure Your Application

Rename the downloaded JSON file to client_secrets.json and place it in the root directory of the cloned project.

### Usage

Run the application with the following command:

`python main.py`

The script will:

Initialize a SQLite database to store album and photo data.
Prompt you to authenticate with Google using your web browser.
Fetch and store albums and photos information in the local database.
