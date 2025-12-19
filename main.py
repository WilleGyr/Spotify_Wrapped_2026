from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ui_utils import set_progress_bars_artists, set_artist_labels, set_progress_bars_songs, set_song_labels, set_top_artist_images, on_tab_changed
from sql_utils import get_top10_artists, get_top10_songs
import sys, time, os, json
from config import AVG_SONG_DURATION
from api_utils import get_spotify_credentials

if __name__ == "__main__":
    #getGoogleSheets_to_sqlite(SPREADSHEET_ID, outDir="data", dbFile="spotify_listenings.db")
    # Load UI
    app = QtWidgets.QApplication(sys.argv)
    base_path = os.path.dirname(__file__)
    ui_path = os.path.join(base_path, "ui/main.ui")
    window = uic.loadUi(ui_path)
    window.LoadingLabel.raise_()
    window.LoadingLabel.show()
    window.show()
    QtWidgets.QApplication.processEvents()
    window.tabWidget.currentChanged.connect(lambda index: on_tab_changed(index, window))

    SPREADSHEET_ID, CLIENT_ID, CLIENT_SECRET = get_spotify_credentials()
    sp=spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))

    set_progress_bars_artists(window, get_top10_artists())
    set_artist_labels(window, get_top10_artists())

    set_progress_bars_songs(window, get_top10_songs())
    set_song_labels(window, get_top10_songs())

    set_top_artist_images(window, get_top10_artists(), sp)
    window.LoadingLabel.hide()
    
    sys.exit(app.exec_())