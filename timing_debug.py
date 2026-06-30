import sys
import curveutils
import qt_scheduler as timing2
import power_supply_drivers.wrapper as coms
from PySide6.QtWidgets import QApplication
import time
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, QTimer, Signal, QRunnable, QThreadPool
import signal

supply = coms.SupplyCommunication("10.30.0.110", lookup = "tti", port = 9221, type="VISA") # connect to power supply with this IP Address
#create two vectors and populate them with the values from a one diode model
U_1, I_1 = curveutils.solarIV(4, 50, 8.75e-3, 4.0, 25.7e-3, 3e-3, 1000, 10000)
#prepare data before running the controll algorithm, removes too low 
U_1, I_1 = curveutils.min_remover(U_1, I_1, 5)
U_1, I_1 = curveutils.stepsize_reducer(list(U_1), list(I_1), 0.025, 'right')

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
    period_s=0.005,
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
app = QApplication(sys.argv)


supply.setValues(5, I_1.max()*1.1, 3000.0)


sched.start_all()

# await a keyboard interrupt and exit cleanly if one is cought
def on_sigint(*_):
    sched.stop()
    app.quit()

signal.signal(signal.SIGINT, on_sigint)

sched.start_all()
app.exec()
