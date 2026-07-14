"""
To whever is cursed to edit this after I'm gone, Professor Teigelkötter told me that this programm is irrelevant and that I should do
it past work hours. I'm not getting payed, I have to spend time outside of my studies to get the funds for my studies. I'm tired of 
this. These guys wanted me gone from day one. Think about your situation. Is your time worthless? Should your efforts always
be in vain? Then stay here and keep working for this guy. I won't. 
"""
import gui_signals, qt_scheduler
import signal
from PySide6.QtWidgets import QApplication

sched = gui_signals.scheduling.scheduler

app = QApplication([])
gui_window = gui_signals.MainDialog(gui_signals.scheduling)
gui_window.show()

sched.start_all()

# await a keyboard interrupt and exit cleanly if one is cought
def on_sigint(*_):
    sched.stop()
    app.quit()

signal.signal(signal.SIGINT, on_sigint)

sched.start_all()
app.exec()