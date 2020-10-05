from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

app = QApplication([])
window = uic.loadUi("Terapsi_Window.ui")
window.show()

exit(app.exec_())
