from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QPropertyAnimation, QTimer
import requests, traceback
from config import AVG_SONG_DURATION
from api_utils import get_artist_image_url, download_image_bytes, find_best_artist, get_artist_id
from sql_utils import (
    get_top10_artists, get_top10_songs,
    get_total_plays, get_unique_artists_count, get_unique_songs_count,
    get_avg_plays_per_day, get_monthly_plays, get_top_artist_song_count,
    calc_listening_time_year,
)

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
            labels[i].setText(f"{artist_name} ({play_count*AVG_SONG_DURATION:.0f} min / {play_count} plays)")

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
            labels[i].setText(f"{song_title} - {artist_name} ({play_count*AVG_SONG_DURATION:.0f} min / {play_count} plays)")

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

def set_top_song_images(window, top_10_songs, sp):
    image_labels = [
        window.TopSong1Image, window.TopSong2Image, window.TopSong3Image,
        window.TopSong4Image, window.TopSong5Image, window.TopSong6Image,
        window.TopSong7Image, window.TopSong8Image, window.TopSong9Image,
        window.TopSong10Image
    ]

    for i, (song_title, artist_name, _) in enumerate(top_10_songs):
        if i >= len(image_labels):
            break

        label = image_labels[i]
        label.clear()
        label.setText("")

        try:
            query = f'track:"{song_title}" artist:"{artist_name}"'
            results = sp.search(q=query, type="track", limit=10)
            items = results["tracks"]["items"]

            if not items:
                label.setText("No track")
                continue

            best = max(items, key=lambda t: t.get("popularity", 0))
            album = best.get("album", {})
            images = album.get("images", [])

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
            print(f"[Image error] {artist_name} - {song_title}: {e}")

def _load_pixmap_from_url(url):
    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    px = QPixmap()
    px.loadFromData(r.content)
    return px

def set_stat_values(window, sp):
    from PyQt5.QtCore import Qt

    top_artists = get_top10_artists()
    top_songs = get_top10_songs()
    total_plays = get_total_plays()
    unique_songs = get_unique_songs_count()
    unique_artists = get_unique_artists_count()
    avg_per_day = get_avg_plays_per_day()
    top_artist_name, top_artist_unique_songs = get_top_artist_song_count()
    minutes = calc_listening_time_year(2026)
    monthly = get_monthly_plays(2026)

    window.TopArtistStat.setText(top_artists[0][0] if top_artists else "N/A")
    window.TopSongStat.setText(top_songs[0][0] if top_songs else "N/A")
    window.MinutesStat.setText(f"{minutes:,.0f}")
    window.HoursStat.setText(f"{minutes / 60:,.0f}")
    window.TotalPlaysStat.setText(f"{total_plays:,}")
    window.SongsStat.setText(f"{unique_songs:,}")
    window.ArtistsStat.setText(f"{unique_artists:,}")
    window.AvgDayStat.setText(f"{avg_per_day * AVG_SONG_DURATION:.1f}")
    window.TopArtistSongsStat.setText(f"{top_artist_unique_songs}")

    # Song card labels
    if top_songs:
        song_title, song_artist, song_plays = top_songs[0]
        window.StatsSongNameStat.setText(song_title)
        window.StatsSongArtistStat.setText(song_artist)
        window.StatsSongPlaysLabel.setText(f"{song_plays} plays · ~{song_plays * AVG_SONG_DURATION:.0f} min")

    # Artist backdrop image
    if top_artists:
        artist_name = top_artists[0][0]
        try:
            results = sp.search(q=f'artist:"{artist_name}"', type="artist", limit=10)
            items = results["artists"]["items"]
            if items:
                best = max(items, key=lambda a: a.get("popularity", 0))
                images = best.get("images", [])
                if images:
                    px = _load_pixmap_from_url(images[0]["url"])
                    lbl = window.StatsArtistImage
                    scaled = px.scaled(lbl.width(), lbl.height(),
                                       Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    # centre-crop to label size
                    x_off = max(0, (scaled.width() - lbl.width()) // 2)
                    y_off = max(0, (scaled.height() - lbl.height()) // 2)
                    cropped = scaled.copy(x_off, y_off, lbl.width(), lbl.height())
                    lbl.setPixmap(cropped)
        except Exception as e:
            print(f"[Stats artist image] {e}")

    # Song album art
    if top_songs:
        song_title, song_artist, _ = top_songs[0]
        try:
            results = sp.search(q=f'track:"{song_title}" artist:"{song_artist}"', type="track", limit=10)
            items = results["tracks"]["items"]
            if items:
                best = max(items, key=lambda t: t.get("popularity", 0))
                images = best.get("album", {}).get("images", [])
                if images:
                    px = _load_pixmap_from_url(images[0]["url"])
                    lbl = window.StatsSongAlbumImage
                    scaled = px.scaled(lbl.width(), lbl.height(),
                                       Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    lbl.setPixmap(scaled)
                    lbl.setAlignment(Qt.AlignCenter)
        except Exception as e:
            print(f"[Stats song image] {e}")

    month_bars = [
        window.MonthJanBar, window.MonthFebBar, window.MonthMarBar,
        window.MonthAprBar, window.MonthMayBar, window.MonthJunBar,
        window.MonthJulBar, window.MonthAugBar, window.MonthSepBar,
        window.MonthOctBar, window.MonthNovBar, window.MonthDecBar,
    ]
    max_month = max(monthly) if any(monthly) else 1
    window._month_bar_animations = []
    for bar, plays in zip(month_bars, monthly):
        pct = int((plays / max_month) * 100)
        anim = QPropertyAnimation(bar, b"value")
        anim.setDuration(max(80, int(1000 * (pct / 100))))
        anim.setStartValue(0)
        anim.setEndValue(pct)
        anim.start()
        window._month_bar_animations.append(anim)