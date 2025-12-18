from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QTimer
import requests, traceback
from config import AVG_SONG_DURATION
from api_utils import get_artist_image_url, download_image_bytes, find_best_artist, get_artist_id
from sql_utils import get_top10_artists, get_top10_songs

def on_tab_changed(index, window):
    page = window.tabWidget.widget(index)

    if page is window.Songs:
        QTimer.singleShot(0, lambda: set_progress_bars_songs(window, get_top10_songs()))
    elif page is window.Artists:
        QTimer.singleShot(0, lambda: set_progress_bars_artists(window, get_top10_artists()))

def set_progress_bars_artists(window, top_artists):
    # top_artists is a list of tuples: (artist_name, play_count)
    progress_bars = [
        window.TopArtist1Bar,
        window.TopArtist2Bar,
        window.TopArtist3Bar,
        window.TopArtist4Bar,
        window.TopArtist5Bar,
        window.TopArtist6Bar,
        window.TopArtist7Bar,
        window.TopArtist8Bar,
        window.TopArtist9Bar,
        window.TopArtist10Bar
    ]

    # Find the maximum play count for scaling
    max_count = top_artists[0][1] if top_artists else 100

    # Keep references so animations are not garbage-collected
    window._artist_bar_animations = []

    for i, (_, play_count) in enumerate(top_artists):
        if i >= len(progress_bars):
            break

        bar = progress_bars[i]

        # Scale the play count to a percentage (0-100)
        percentage = int((play_count / max_count) * 100)
        duration = max(50, int(1200 * (percentage / 100)))

        animation = QPropertyAnimation(bar, b"value")
        animation.setDuration(duration)     # ms
        animation.setStartValue(0)
        animation.setEndValue(percentage)
        animation.start()

        window._artist_bar_animations.append(animation)

def set_progress_bars_songs(window, top_songs):
    # top_songs is a list of tuples: (song_title, artist_name, play_count)
    progress_bars = [
        window.TopSong1Bar,
        window.TopSong2Bar,
        window.TopSong3Bar,
        window.TopSong4Bar,
        window.TopSong5Bar,
        window.TopSong6Bar,
        window.TopSong7Bar,
        window.TopSong8Bar,
        window.TopSong9Bar,
        window.TopSong10Bar
    ]

    # Find the maximum play count for scaling
    max_count = top_songs[0][2] if top_songs else 100

    # Keep references so animations don’t get garbage-collected
    window._song_bar_animations = []

    for i, (_, _, play_count) in enumerate(top_songs):
        if i >= len(progress_bars):
            break

        bar = progress_bars[i]

        # Scale the play count to a percentage (0-100)
        percentage = int((play_count / max_count) * 100)
        duration = max(50, int(1200 * (percentage / 100)))

        animation = QPropertyAnimation(bar, b"value")
        animation.setDuration(duration)          # ms
        animation.setStartValue(0)
        animation.setEndValue(percentage)
        animation.start()

        window._song_bar_animations.append(animation)


def set_artist_labels(window, top_artists):
    # top_artists is a list of tuples: (artist_name, play_count)
    labels = [
        window.TopArtist1Label,
        window.TopArtist2Label,
        window.TopArtist3Label,
        window.TopArtist4Label,
        window.TopArtist5Label,
        window.TopArtist6Label,
        window.TopArtist7Label,
        window.TopArtist8Label,
        window.TopArtist9Label,
        window.TopArtist10Label
    ]
    
    for i, (artist_name, play_count) in enumerate(top_artists):
        if i < len(labels):
            labels[i].setText(f"{artist_name} ({play_count*AVG_SONG_DURATION:.0f} min)")

def set_song_labels(window, top_songs):
    # top_songs is a list of tuples: (song_title, artist_name, play_count)
    labels = [
        window.TopSong1Label,
        window.TopSong2Label,
        window.TopSong3Label,
        window.TopSong4Label,
        window.TopSong5Label,
        window.TopSong6Label,
        window.TopSong7Label,
        window.TopSong8Label,
        window.TopSong9Label,
        window.TopSong10Label
    ]
    
    for i, (song_title, artist_name, play_count) in enumerate(top_songs):
        if i < len(labels):
            labels[i].setText(f"{song_title} - {artist_name} ({play_count*AVG_SONG_DURATION:.0f} min)")

def set_top_artist_images(window, top_10_artists, sp):
    image_labels = [
        window.TopArtist1Image, window.TopArtist2Image, window.TopArtist3Image,
        window.TopArtist4Image, window.TopArtist5Image, window.TopArtist6Image,
        window.TopArtist7Image, window.TopArtist8Image, window.TopArtist9Image,
        window.TopArtist10Image
    ]

    for i, (artist_name, _) in enumerate(top_10_artists):
        if i >= len(image_labels):
            break

        label = image_labels[i]
        label.clear()
        label.setText("")

        try:
            # Get more than 1 result so we can avoid wrong matches (e.g., Adele)
            results = sp.search(q=f'artist:"{artist_name}"', type="artist", limit=10)
            items = results["artists"]["items"]

            if not items:
                label.setText("No artist")
                continue

            # Pick the most likely "official" artist (usually highest popularity)
            best = max(items, key=lambda a: a.get("popularity", 0))

            images = best.get("images", [])
            if not images:
                label.setText("No image")
                continue

            image_url = images[0]["url"]  # largest

            r = requests.get(image_url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()

            px = QPixmap()
            if not px.loadFromData(r.content):
                label.setText("Bad image")
                continue

            label.setPixmap(px)
            label.setScaledContents(True)

        except Exception as e:
            label.setText("Image error")
            print(f"[Image error] {artist_name}: {e}")