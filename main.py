import numpy as np
import power_supply_drivers.wrapper as coms
import curveutils
from PySide6.QtCore import QObject, QTimer, Signal, QRunnable, QThreadPool
import signal
import qt_scheduler as timing2
from PySide6.QtWidgets import QApplication
from PySide6 import QtWidgets
import sys
import gui
supply = coms.SupplyCommunication("10.30.0.110", lookup = "tti", port = 9221, type="VISA") # connect to power supply with this IP Address

#create two vectors and populate them with the values from a one diode model
U_1, I_1 = curveutils.solarIV(4, 50, 8.75e-3, 4.0, 25.7e-3, 3e-3, 1000, 10000)
#prepare data before running the controll algorithm, removes too low 
U_1, I_1 = curveutils.min_remover(U_1, I_1, 5)
U_1, I_1 = curveutils.stepsize_reducer(list(U_1), list(I_1), 0.025, 'right')

set_supply = curveutils.setter(U_1, I_1)

class MainDialog(QtWidgets.QDialog):
    """
    This class wraps the gui.py file into a new QDialog, this way the singals and connections can be handled without directly editing gui.py.
    """
    def __init__(self, parent = None):
        super().__init__(parent)

        self.ui = gui.Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.voltage_display.value


#eddited the value of the initial voltage to 5, by suggestion by Rüdiger Mann 27.04.26
supply.setValues(5, I_1.max()*1.1, 3000.0)

set_supply = curveutils.setter(U_1, I_1)

def measure(supply):
    supply.measureValues()
    # supply.write/setpoints...
    #print(supply.measuredpoints)
    return
def set(supply, setter):
    supply.setValues(setter.u_for_i_incremental(supply.measuredpoints.current))
    return
    
def print_measured_points(supply):
    print(supply.measuredpoints)
    return
psu_com = timing2.semaphore(semaphore_name="psu_com")

set_supply = curveutils.setter(U_1, I_1)
sched = timing2.Scheduler(tick_ms=1)
sched.add_periodic(
    "measure",
    period_s=0.01,
    func=measure,
    args=(supply,),          # only supply is static
    kwargs={},
    start_immediately=True,
    semaphores=[psu_com]
)
sched.add_periodic(
    "set",
    period_s=0.01,
    func=set,
    args=(supply,set_supply,),          # only supply is static
    kwargs={},
    start_immediately=True,
    semaphores=[psu_com]
)
sched.add_periodic(
    "print",
    period_s=1,
    func=print_measured_points,
    args=(supply,),          # only supply is static
    kwargs={},
    start_immediately=True
)
app = QApplication([])
gui_window = MainDialog()
gui_window.show()


supply.setValues(5, I_1.max()*1.1, 3000.0)


sched.start_all()

# await a keyboard interrupt and exit cleanly if one is cought
def on_sigint(*_):
    sched.stop()
    app.quit()

signal.signal(signal.SIGINT, on_sigint)

sched.start_all()
app.exec()



#coms.closeSocket(socket)