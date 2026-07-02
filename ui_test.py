from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,  QWidget
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

app = QApplication([])

window = QMainWindow()
# doesn't work on linux at all, doesn't work properly on windows, can't be fixed, no one cares about his issue either fuck it
test = QIcon("solar_energy_icon.png")
window.setWindowIcon(test)
window.setMinimumSize(500,500)

layout =QVBoxLayout()

window.setWindowTitle("SunCell")

button_1 = QPushButton("Button 1")
button_2 = QPushButton("Button 2")

centerWidget = QWidget()
centerWidget.setLayout(layout)

window.setCentralWidget(centerWidget)

window.show()
app.exec()