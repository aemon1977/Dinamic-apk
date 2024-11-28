from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow

app = QApplication([])
window = QMainWindow()
uic.loadUi("example.ui", window)
window.show()
app.exec_()
