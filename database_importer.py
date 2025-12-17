import os
import sys
import csv
import sqlite3
import requests
from datetime import datetime
from config import SPREADSHEET_ID

def _parse_dt(value: str) -> str:
    value = (value or "").strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
    ):
        try:
            return datetime.strptime(value, fmt).isoformat(sep=" ")
        except ValueError:
            pass
    return value  # fallback

def getGoogleSheets_to_sqlite(spreadsheet_ids, outDir=None, dbFile="spotify.db"):
    if outDir:
        os.makedirs(outDir, exist_ok=True)
        db_path = os.path.join(outDir, dbFile)
    else:
        db_path = dbFile

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode = WAL;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS listenings (
            id INTEGER PRIMARY KEY,
            listened_at TEXT NOT NULL,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            spotify_id TEXT,
            url TEXT,
            source_sheet_id TEXT,
            UNIQUE(listened_at, title, artist, spotify_id, url)
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listenings_listened_at ON listenings(listened_at);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listenings_spotify_id ON listenings(spotify_id);")

    inserted_total = 0
    parsed_total = 0

    for i, sheet_id in enumerate(spreadsheet_ids):
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error downloading Google Sheet with ID {sheet_id}: {response.status_code}")
            conn.close()
            sys.exit(1)

        # Optional guard: helps detect "HTML login page but status 200"
        if "text/csv" not in response.headers.get("Content-Type", ""):
            print(f"Sheet {sheet_id}: did not return CSV (maybe private/not published). "
                  f"Content-Type={response.headers.get('Content-Type')}")
            conn.close()
            sys.exit(1)

        content = response.content.decode("utf-8")
        reader = csv.reader(content.splitlines())

        rows = []
        for row in reader:
            # Expect exactly 5 columns (but we’ll be tolerant)
            if not row or all((c or "").strip() == "" for c in row):
                continue

            # pad short rows to length 5
            row = (row + ["", "", "", "", ""])[:5]

            listened_at = _parse_dt(row[0])
            title = (row[1] or "").strip()
            artist = (row[2] or "").strip()
            spotify_id = (row[3] or "").strip() or None
            track_url = (row[4] or "").strip() or None

            if not listened_at or not title or not artist:
                continue

            rows.append((listened_at, title, artist, spotify_id, track_url, sheet_id))

        parsed_total += len(rows)

        before = conn.total_changes
        with conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO listenings
                (listened_at, title, artist, spotify_id, url, source_sheet_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows
            )
        inserted = conn.total_changes - before
        inserted_total += inserted

        print(f"Imported sheet {i+1}/{len(spreadsheet_ids)} "
              f"(parsed {len(rows)}, inserted {inserted}, duplicates {len(rows) - inserted})")

    conn.close()
    print(f"\nDone. Database saved to: {db_path}")
    print(f"Parsed total: {parsed_total}, Inserted new: {inserted_total}, Duplicates ignored: {parsed_total - inserted_total}")
    return db_path


if __name__ == "__main__":
    # Example usage
    getGoogleSheets_to_sqlite(SPREADSHEET_ID, outDir="data", dbFile="spotify_listenings.db")
