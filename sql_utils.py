import sqlite3
from config import AVG_SONG_DURATION

def calc_listening_time_year(year: int):
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM listenings
        WHERE listened_at LIKE ?;
    """, (f'%{year} at %',))
    row_count = cursor.fetchone()[0]
    duration = row_count * AVG_SONG_DURATION
    conn.close()
    
    return duration

def calc_listening_time_month(month: int, year: int):
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month - 1]
    
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM listenings
        WHERE listened_at LIKE ?;
    """, (f'{month_name}%, {year} at %',))
    row_count = cursor.fetchone()[0]
    duration = row_count * AVG_SONG_DURATION
    conn.close()
    
    return duration

def get_top10_artists():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artist, COUNT(*) as play_count FROM listenings
        GROUP BY artist
        ORDER BY play_count DESC
        LIMIT 10;
    """)
    top_artists = cursor.fetchall()
    conn.close()
    
    return top_artists

def get_top10_songs():
    conn = sqlite3.connect("data/spotify_listenings.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, artist, COUNT(*) as play_count FROM listenings
        GROUP BY title, artist
        ORDER BY play_count DESC
        LIMIT 10;
    """)
    top_songs = cursor.fetchall()
    conn.close()
    
    return top_songs

print(calc_listening_time_year(2025))
print(calc_listening_time_month(2, 2025))
print(get_top10_artists())
print(get_top10_songs())