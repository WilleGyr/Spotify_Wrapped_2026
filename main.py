from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QVBoxLayout
from api_utils import get_spotify_credentials
from database_importer import getGoogleSheets_to_sqlite
from ui_utils import set_progress_bars, set_artist_labels
from sql_utils import get_top10_artists, get_top10_songs
import sys, time, os, json
from config import AVG_SONG_DURATION, SPREADSHEET_ID, CLIENT_ID, CLIENT_SECRET

if __name__ == "__main__":
    #getGoogleSheets_to_sqlite(SPREADSHEET_ID, outDir="data", dbFile="spotify_listenings.db")

    # Load UI
    app = QtWidgets.QApplication(sys.argv)
    base_path = os.path.dirname(__file__)
    ui_path = os.path.join(base_path, "ui/main.ui")
    window = uic.loadUi(ui_path)
    window.show()

    set_progress_bars(window, get_top10_artists())
    set_artist_labels(window, get_top10_artists())
    
    sys.exit(app.exec_())