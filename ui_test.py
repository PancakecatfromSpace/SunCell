from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon

app = QApplication([])

window = QMainWindow()
fuck_shit = QIcon("solar_energy_icon.png")
window.setWindowIcon(fuck_shit)
window.setMinimumSize(250,500)

window.setWindowTitle("SunCell")


window.show()
app.exec()