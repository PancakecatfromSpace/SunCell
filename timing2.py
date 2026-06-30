import time
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, QTimer, Signal, QRunnable, QThreadPool

@dataclass
class semaphore:
    semaphore_name:str=None
    semaphore_set:bool=False
    semaphore_held_since:float=None

@dataclass
class Job:
    name: str
    period_s: float
    func: callable
    args: tuple = field(default_factory=tuple)     # static args
    kwargs: dict = field(default_factory=dict)    # static kwargs
    semaphores: list[semaphore] = field(default_factory=list)
    next_deadline: float = 0.0

class JobSignals(QObject):
    finished = Signal(str, object)
    failed = Signal(str, str)

class PSURunnable(QRunnable):
    def __init__(self, job_name, now, func, args, kwargs):
        super().__init__()
        self.job_name = job_name
        self.now = now
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = JobSignals()

    def run(self):
        # attempt to run the job, if the job fails output message properly
        try:
            res = self.func(*self.args, self.job_name, self.now, **self.kwargs)
            self.signals.finished.emit(self.job_name, res)
        except Exception as e:
            self.signals.failed.emit(self.job_name, repr(e))

class Scheduler(QObject):
    def __init__(self, tick_ms=20, parent=None):
        super().__init__(parent)
        self._tick = QTimer(self)
        self._tick.setInterval(tick_ms)
        self._tick.timeout.connect(self._on_tick)

        self._jobs: list[Job] = []
        self._started = False

        self._pool = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(1)  # serialize PSU calls

    def add_periodic(self, name, period_s, func, *, args=(), kwargs=None, semaphores: list[semaphore] = None,start_immediately=False):
        if kwargs is None:
            kwargs = {}
        now = time.monotonic()
        next_deadline = now if start_immediately else (now + period_s)
        self._jobs.append(Job(name=name, period_s=period_s, func=func,
                               args=args, kwargs=kwargs, semaphores=semaphores, next_deadline=next_deadline))

    def start_all(self):
        if self._started:
            return
        self._started = True
        self._tick.start()

    def _on_tick(self):
        now = time.monotonic()
        for job in self._jobs:
            if now >= job.next_deadline:
                elapsed = int((now - job.next_deadline) / job.period_s) + 1
                job.next_deadline += elapsed * job.period_s

                runnable = PSURunnable(job.name, now, job.func, job.args, job.kwargs)
                runnable.signals.failed.connect(lambda name, err: print(f"{name} failed: {err}"))
                self._pool.start(runnable)
