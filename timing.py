"""
Functions and classes to call the classes and functions from curveutils in a time sensible way.
Contains the dataclass Job, which contains the necessary informations for creating a job
"""
from dataclasses import dataclass
import time
from PySide6.QtCore import QObject, QTimer, Signal, QRunnable, QThreadPool, Slot

@dataclass
class Job:
    name: str
    period_s: float
    callback: callable
    next_deadline: float = 0.0

class Scheduler(QObject):
    job_due = Signal(str)  # optional: for UI-safe dispatch

    def __init__(self, tick_ms=20, parent=None):
        super().__init__(parent)
        self._tick = QTimer(self)
        self._tick.setInterval(tick_ms)
        # connect the _on_tick method to the _tick_timeout, this will ensure the interrupt caused by running past the timeout will trigger the appropriate list of jobs
        self._tick.timeout.connect(self._on_tick)
        self._jobs: list[Job] = []
        self._started = False

    def add_periodic(self, name, period_s, callback, *, start_immediately=False):
        """
        Adds a new periodic job to the 
        """
        now = time.monotonic()
        next_deadline = now if start_immediately else (now + period_s)
        self._jobs.append(Job(name, period_s, callback, next_deadline))

    def start_all(self):
        """
        Start all timed jobs, if all jobs already started, does nothing and returns.
        """
        if self._started:
            return
        self._started = True
        self._tick.start()

    def stop_all(self):
        """
        Stops the timer connected to all jobs.
        """
        self._tick.stop()
        self._started = False

    def _on_tick(self):
        """
        _on_tick is executed every time the Qtimer times out which is set by the varaible tick_ms 
        """
        # now is a time stamp given to each job, it describes when the job was last run
        now = time.monotonic()
        for job in self._jobs:
            if now >= job.next_deadline:
                # Prevent drift: schedule next deadline relative to the old one
                # (not relative to "now")
                elapsed_periods = int((now - job.next_deadline) / job.period_s) + 1
                job.next_deadline += elapsed_periods * job.period_s

                # If callback is heavy, consider emitting a signal and handling in a worker thread.
                job.callback(job.name, now)

def read_current(name, t, supply):
    # read measured current, compute voltage, send to PSU
    supply.measureValues()
    #print(supply.setpoints)
    pass

class QJob(QRunnable):
    """
    Define a function as a QRunnable to later add them to the QThreadPool.
    Args:

    """
    @Slot()
    def __init__(self, fn, name:str, period_s:float, callback:callable, *args, **kwargs):
        # adds following arguments to the parrent class QRunnable
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

        self.name = name
        self.period_s = period_s
        self.callback = callback
        self.next_deadline: float = 0.0

    def run(self):
        self.fn(*self.args, **self.kwargs)