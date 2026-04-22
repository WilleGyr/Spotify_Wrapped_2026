import sqlite3
from config import AVG_SONG_DURATION

YEAR = 2026
_YEAR_FILTER = f'%, {YEAR} at %'

def get_total_plays():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM listenings WHERE listened_at LIKE ?", (_YEAR_FILTER,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_unique_artists_count():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT artist) FROM listenings WHERE listened_at LIKE ?", (_YEAR_FILTER,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_unique_songs_count():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT title) FROM listenings WHERE listened_at LIKE ?", (_YEAR_FILTER,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_avg_plays_per_day():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM listenings WHERE listened_at LIKE ?", (_YEAR_FILTER,))
    total = cursor.fetchone()[0]
    cursor.execute("""
        SELECT COUNT(DISTINCT substr(listened_at, 1, instr(listened_at, ' at ') - 1))
        FROM listenings WHERE listened_at LIKE ?
    """, (_YEAR_FILTER,))
    days = cursor.fetchone()[0]
    conn.close()
    return total / days if days > 0 else 0

def get_monthly_plays(year: int):
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    monthly = []
    for month_name in month_names:
        cursor.execute(
            "SELECT COUNT(*) FROM listenings WHERE listened_at LIKE ?",
            (f'{month_name}%, {year} at %',)
        )
        monthly.append(cursor.fetchone()[0])
    conn.close()
    return monthly

def get_top_artist_song_count():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artist FROM listenings WHERE listened_at LIKE ?
        GROUP BY artist ORDER BY COUNT(*) DESC LIMIT 1
    """, (_YEAR_FILTER,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return ("N/A", 0)
    artist_name = row[0]
    cursor.execute(
        "SELECT COUNT(DISTINCT title) FROM listenings WHERE artist = ? AND listened_at LIKE ?",
        (artist_name, _YEAR_FILTER)
    )
    song_count = cursor.fetchone()[0]
    conn.close()
    return (artist_name, song_count)

def calc_listening_time_year(year: int):
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM listenings WHERE listened_at LIKE ?",
        (f'%, {year} at %',)
    )
    row_count = cursor.fetchone()[0]
    conn.close()
    return row_count * AVG_SONG_DURATION

def calc_listening_time_month(month: int, year: int):
    month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month - 1]
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM listenings WHERE listened_at LIKE ?",
        (f'{month_name}%, {year} at %',)
    )
    row_count = cursor.fetchone()[0]
    conn.close()
    return row_count * AVG_SONG_DURATION

def get_top10_artists():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artist, COUNT(*) as play_count FROM listenings
        WHERE listened_at LIKE ?
        GROUP BY artist
        ORDER BY play_count DESC
        LIMIT 10
    """, (_YEAR_FILTER,))
    top_artists = cursor.fetchall()
    conn.close()
    return top_artists

def get_top10_songs():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, artist, COUNT(*) as play_count FROM listenings
        WHERE listened_at LIKE ?
        GROUP BY title, artist
        ORDER BY play_count DESC
        LIMIT 10
    """, (_YEAR_FILTER,))
    top_songs = cursor.fetchall()
    conn.close()
    return top_songs
