from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon

app = QApplication([])

window = QMainWindow()
test = QIcon("solar_energy_icon.ico")
window.setWindowIcon(test)
window.setMinimumSize(250,500)

window.setWindowTitle("SunCell")
print("isNull:", test.isNull())


window.show()
app.exec()