import os, spotipy, requests, re, unicodedata
from spotipy.oauth2 import SpotifyClientCredentials
from config import ARTIST_ID_OVERRIDES
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

def get_artist_image_url(artist_name: str) -> tuple[str | None, str | None]:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)  # Search endpoint :contentReference[oaicite:2]{index=2}
    items = results["artists"]["items"]
    if not items:
        return None, None

    artist = items[0]
    images = artist.get("images", [])
    img_url = images[0]["url"] if images else None  # widest first :contentReference[oaicite:3]{index=3}
    spotify_link = artist["external_urls"]["spotify"]
    return img_url, spotify_link

def download_image_bytes(url: str) -> bytes:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.content

def _norm(s: str) -> str:
    # normalize accents + whitespace + case
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s.strip().lower())
    return s

def find_best_artist(sp, artist_name: str):
    q = f'artist:"{artist_name}"'   # quoted: helps reduce partial matches
    results = sp.search(q=q, type="artist", limit=10)

    items = results["artists"]["items"]
    if not items:
        return None

    target = _norm(artist_name)

    # Prefer exact name matches first
    exact = [a for a in items if _norm(a.get("name", "")) == target]
    candidates = exact if exact else items

    # Pick the “most real” one (usually highest popularity, then followers)
    def score(a):
        pop = a.get("popularity", 0)
        followers = (a.get("followers") or {}).get("total", 0)
        return (pop, followers)

    return max(candidates, key=score)

def get_artist_id(sp, artist_name: str):
    key = artist_name.strip().lower()
    if key in ARTIST_ID_OVERRIDES:
        return ARTIST_ID_OVERRIDES[key]
    artist = find_best_artist(sp, artist_name)
    print(f"Resolved artist '{artist_name}' to ID: {artist['id'] if artist else 'None'}")
    return artist["id"] if artist else None