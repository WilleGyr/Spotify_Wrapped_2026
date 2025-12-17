from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout
from config import AVG_SONG_DURATION

def set_progress_bars(window, top_artists):
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
    
    for i, (artist_name, play_count) in enumerate(top_artists):
        if i < len(progress_bars):
            # Scale the play count to a percentage (0-100)
            percentage = int((play_count / max_count) * 100)
            progress_bars[i].setValue(percentage)

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