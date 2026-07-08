import gui_signals, qt_scheduler
import signal
from PySide6.QtWidgets import QApplication
"""
def set(supply, setter):
    supply.setValues(setter.u_for_i_incremental(supply.measuredpoints.current))
    return
""" 
def print_measured_points(supply):
    print(supply.measuredpoints)
    return
    
psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")

sched = qt_scheduler.Scheduler(tick_ms=1)
sched.add_periodic(
    "measure",
    period_s=0.01,
    func=gui_signals.measure_signal.measure_emit_set,
    args=(),          # only supply is static
    kwargs={},
    start_immediately=True,
    semaphores=[psu_com]
)
"""
sched.add_periodic(
    "set",
    period_s=0.01,
    func=set,
    args=(gui_signals.supply,gui_signals.set_supply,),          # only supply is static
    kwargs={},
    start_immediately=True,
    semaphores=[psu_com]
)
"""
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

sched.start_all()

# await a keyboard interrupt and exit cleanly if one is cought
def on_sigint(*_):
    sched.stop()
    app.quit()

signal.signal(signal.SIGINT, on_sigint)

sched.start_all()
app.exec()