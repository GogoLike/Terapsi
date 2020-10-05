from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
import sqlite3


# =====================================================================================================================

class TerapsiDB:
    def __init__(self):
        self.conn = sqlite3.connect("""Terapsi.db""")
        self.cursor = self.conn.cursor()


# =====================================================================================================================

def print_hi():
    print("Hi!")


# =====================================================================================================================


# =====================================================================================================================

print("""Terapsi has started""")

database = TerapsiDB()

app = QApplication([])
window = uic.loadUi("Terapsi_Window.ui")
window.show()

window.actionOpen.triggered.connect(print_hi)

exit(app.exec_())
