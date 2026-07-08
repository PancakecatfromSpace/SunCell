"""
To whever is cursed to edit this after I'm gone, Professor Teigelkötter told me that this programm is irrelevant and that I should do
it past work hours. I'm not getting payed, I have to spend time outside of my studies to get the funds for my studies. I'm tired of 
this. These guys wanted me gone from day one. Think about your situation. Is your time worthless? Should your efforts always
be in vain? Then stay here and keep working for this guy. I won't.
"""

import gui_signals, qt_scheduler
import signal
from PySide6.QtWidgets import QApplication

def print_measured_points(supply):
    print(supply.measuredpoints)
    return
def print_once():
    print("This only ran once.")
    return
    
psu_com = qt_scheduler.semaphore(semaphore_name="psu_com")

sched = gui_signals.sched
sched.add_periodic(
    "measure_set",
    period_s=0.01,
    func=gui_signals.measure_signal.measure_emit_set,
    args=(),          # only supply is static
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
sched.add_periodic(
    "print_once",
    period_s=0,
    func=print_once,
    args=(),          # only supply is static
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