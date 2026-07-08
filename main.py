import curveutils, gui_signals, qt_scheduler
import signal
from PySide6.QtWidgets import QApplication
 # connect to power supply with this IP Address

#create two vectors and populate them with the values from a one diode model
U_1, I_1 = curveutils.solarIV(4, 50, 8.75e-3, 4.0, 25.7e-3, 3e-3, 1000, 10000)
#prepare data before running the controll algorithm, removes too low 
U_1, I_1 = curveutils.min_remover(U_1, I_1, 5)
U_1, I_1 = curveutils.stepsize_reducer(list(U_1), list(I_1), 0.025, 'right')

#eddited the value of the initial voltage to 5, by suggestion by Rüdiger Mann 27.04.26
gui_signals.supply.setValues(5, I_1.max()*1.1, 3000.0)

set_supply = curveutils.setter(U_1, I_1)

def set(supply, setter):
    supply.setValues(setter.u_for_i_incremental(supply.measuredpoints.current))
    return
    
def print_measured_points(supply):
    print(supply.measuredpoints)
    return
    
psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")

set_supply = curveutils.setter(U_1, I_1)
sched = qt_scheduler.Scheduler(tick_ms=1)
sched.add_periodic(
    "measure",
    period_s=0.01,
    func=gui_signals.measure_signal.emit_new_values,
    args=(),          # only supply is static
    kwargs={},
    start_immediately=True,
    semaphores=[psu_com]
)
sched.add_periodic(
    "set",
    period_s=0.01,
    func=set,
    args=(gui_signals.supply,set_supply,),          # only supply is static
    kwargs={},
    start_immediately=True,
    semaphores=[psu_com]
)
sched.add_periodic(
    "print",
    period_s=1,
    func=print_measured_points,
    args=(gui_signals.supply,),          # only supply is static
    kwargs={},
    start_immediately=True
)
app = QApplication([])
gui_window = gui_signals.MainDialog()
gui_window.show()

gui_signals.supply.setValues(5, I_1.max()*1.1, 3000.0)

sched.start_all()

# await a keyboard interrupt and exit cleanly if one is cought
def on_sigint(*_):
    sched.stop()
    app.quit()

signal.signal(signal.SIGINT, on_sigint)

sched.start_all()
app.exec()