import os
from dotenv import load_dotenv

# Function to import Spotify API credentials from .env file
def get_spotify_credentials1():
    load_dotenv("credentials/spotify_api.env")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    return SPREADSHEET_ID, CLIENT_ID, CLIENT_SECRET

import json

def get_spotify_credentials():
    load_dotenv("credentials/spotify_api.env")
    spreadsheet_ids_raw = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_ids_raw:
        raise ValueError("Missing SPREADSHEET_ID in .env")

    try:
        spreadsheet_ids = json.loads(spreadsheet_ids_raw)  # -> list[str]
    except json.JSONDecodeError as e:
        raise ValueError(
            "SPREADSHEET_ID must be JSON like [\"id1\",\"id2\"]."
        ) from e

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    return spreadsheet_ids, client_id, client_secret
