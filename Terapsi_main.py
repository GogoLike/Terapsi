from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaContent, QMediaPlayer
import sqlite3
import mutagen


# =====================================================================================================================

def getFilesPath():
    files_path = QFileDialog.getOpenFileNames(filter="Audio Files (*.mp3 *.wav)")
    path = files_path[0:-1][0]
    return path


# =====================================================================================================================

class TerapsiDB:

    def __init__(self):
        self.conn = sqlite3.connect("""Terapsi.db""")
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute("""CREATE TABLE Main_Playlist (num integer, song_path text);""")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def rowsCount(self, table):
        self.cursor.execute("""Select Count(*) FROM %s;""" % str(table))
        count = self.cursor.fetchone()[0]
        self.conn.commit()
        return count

    def addMainPlaylist(self):
        for path in getFilesPath():
            self.cursor.execute("""INSERT INTO Main_Playlist (num, song_path) VALUES (%d, '%s');""" % (
                self.rowsCount("Main_Playlist"), str(path)))
            self.conn.commit()

        window.addPlaylistTable()

    def readMainPlaylist(self):
        self.cursor.execute("""SELECT * FROM Main_Playlist;""")
        data = self.cursor.fetchall()
        self.conn.commit()
        return data

    def clearMainPlaylist(self):
        self.cursor.execute("""DELETE FROM Main_Playlist;""")
        self.conn.commit()


# =====================================================================================================================


class Terapsi:

    def __init__(self):
        self.app = QApplication([])
        self.window = uic.loadUi("""Terapsi_Window.ui""")

        self.media_player = QMediaPlayer()
        self.media_playlist = QMediaPlaylist()

        self.fillMediaPlaylist()

        self.media_player.setPlaylist(self.media_playlist)

        self.window.playlist_table.setColumnCount(4)
        self.window.playlist_table.setRowCount(database.rowsCount("Main_Playlist"))

        self.window.playlist_table.horizontalHeader().resizeSection(0, 20)
        self.window.playlist_table.horizontalHeader().resizeSection(1, 420)
        self.window.playlist_table.horizontalHeader().resizeSection(2, 220)
        self.window.playlist_table.horizontalHeader().resizeSection(3, 98)

        self.window.playlist_table.setSelectionMode(QAbstractItemView.NoSelection)

        self.addPlaylistTable()

        self.window.playlist_table.cellClicked.connect(self.quadClicked)

        self.window.actionOpen.triggered.connect(database.addMainPlaylist)

        self.window.play_button.clicked.connect(self.playSong)
        self.window.pause_button.clicked.connect(self.pauseSong)
        self.window.stop_button.clicked.connect(self.stopSong)
        self.window.next_button.clicked.connect(self.nextSong)
        self.window.previous_button.clicked.connect(self.previousSong)
        self.window.clear_button.clicked.connect(self.clearPlaylist)

        self.window.show()

    def addPlaylistTable(self):
        self.window.playlist_table.clear()

        self.fillMediaPlaylist()

        self.window.playlist_table.setRowCount(database.rowsCount("Main_Playlist"))

        main_playlist = database.readMainPlaylist()
        i = 0
        for song in main_playlist:
            song_num = str(int(song[0]) + 1)
            song_path = song[1]
            song_file = mutagen.File(song_path)
            try:
                song_name = str(song_file.tags.getall('TIT2')[0])
            except IndexError:
                song_name = '.'.join(str(song_path).split("/")[-1].split(".")[0:-1])
            try:
                song_singer = str(song_file.tags.getall('TPE1')[0])
            except IndexError:
                song_singer = "Unknown"
            song_duration = '%.2f' % song_file.info.length

            song_num_item = QTableWidgetItem(song_num)
            song_name_item = QTableWidgetItem(song_name)
            song_singer_item = QTableWidgetItem(song_singer)
            song_duration_item = QTableWidgetItem(song_duration)

            song_num_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            song_name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            song_singer_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            song_duration_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            self.window.playlist_table.setItem(i, 0, song_num_item)
            self.window.playlist_table.setItem(i, 1, song_name_item)
            self.window.playlist_table.setItem(i, 2, song_singer_item)
            self.window.playlist_table.setItem(i, 3, song_duration_item)

            i += 1

    def quadClicked(self):
        self.window.playlist_table.clearSelection()

        self.window.playlist_table.setSelectionMode(QAbstractItemView.MultiSelection)

        row_num = self.window.playlist_table.currentRow()
        self.window.playlist_table.selectRow(row_num)

        self.window.playlist_table.setSelectionMode(QAbstractItemView.NoSelection)

    def playSong(self):
        self.media_player.play()
        self.window.play_button.setEnabled(False)
        self.window.pause_button.setEnabled(True)
        self.window.stop_button.setEnabled(True)

    def pauseSong(self):
        self.media_player.pause()
        self.window.play_button.setEnabled(True)
        self.window.pause_button.setEnabled(False)
        self.window.stop_button.setEnabled(True)

    def stopSong(self):
        self.media_player.stop()
        self.window.pause_button.setEnabled(False)
        self.window.stop_button.setEnabled(False)
        self.window.play_button.setEnabled(True)

    def nextSong(self):
        self.media_player.playlist().next()

    def previousSong(self):
        self.media_player.playlist().previous()

    def clearPlaylist(self):
        database.clearMainPlaylist()
        self.window.playlist_table.clear()
        self.media_playlist.clear()
        self.window.playlist_table.setRowCount(database.rowsCount("Main_Playlist"))

    def fillMediaPlaylist(self):
        for path in database.readMainPlaylist():
            url = QUrl("file:///%s" % str(path[1]))
            media = QMediaContent(url)
            self.media_playlist.addMedia(media)


# =====================================================================================================================


print("""Terapsi has started""")

database = TerapsiDB()
window = Terapsi()

exit(window.app.exec_())
