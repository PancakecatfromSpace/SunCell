import time
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, QTimer, Signal, QRunnable, QThreadPool

@dataclass
class semaphore:
    semaphore_name:str=None
    semaphore_set:bool=False
    held_by:str=None

@dataclass
class Job:
    # Structure the job with a list of semaphores and the function to be called upon
    name: str
    period_s: float
    func: callable
    args: tuple = field(default_factory=tuple)     # static args
    kwargs: dict = field(default_factory=dict)    # static kwargs
    semaphores: list[semaphore] = field(default_factory=list)
    next_deadline: float = 0.0

class JobSignals(QObject):
    # store the return signal in finished and failed, the failed part will only be read if executing the jobs func raises an excpetion
    finished = Signal(str, object)
    failed = Signal(str, str)

class PSURunnable(QRunnable):
    """
    Dataclass creating a job from a QRunnable object so they can be scheduled using QThreadPool
    """
    def __init__(self, job: Job, now: float):
        super().__init__()
        self.job = job
        self.now = now
        self.signals = JobSignals()

    def run(self):
        # attempt to run the job, if the job fails output message properly
        try:
            res = self.job.func(*self.job.args, **self.job.kwargs)
            self.signals.finished.emit(self.job.name, res)
        except Exception as e:
            self.signals.failed.emit(self.job.name, repr(e))

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

        self._stoped = False
    def add_periodic(self, name, period_s, func, *, args=(), kwargs=None, semaphores: list[semaphore] = None,start_immediately=False):
        if kwargs is None:
            kwargs = {}
        now = time.monotonic()
        next_deadline = now if start_immediately else (now + period_s)
        self._jobs.append(Job(name=name, period_s=period_s, func=func,
                               args=args, kwargs=kwargs, semaphores=semaphores, next_deadline=next_deadline))

    def start_all(self):
        """
        Start all jobs added via add_periodic.
        """
        # start the tick rate which will trigger _on_tick
        if self._started:
            return
        self._started = True
        self._tick.start()
    def stop(self):
        # stops the tick rate 
        if self._stoped:
            return
        self._stoped = True
        self._tick.stop()
    def __del__(self):
        # when deleted stop the timer, otherwise the qt timer can remain active, which will trigger an exception when it's signal goes nowhere
        try:
            self.stop()
        except:
            pass
    def _on_tick(self):
        # check every tick which jobs are due and run them
        now = time.monotonic()
        # go through _jobs:
        for job in self._jobs:
            if self._stoped:
                return
            # go through all the semaphores of the current job, if it is set by any other job, don't execute the job
            for semaphores in job.semaphores:

                return
            # exit tick if stoped is set, this prevents an issue if the tick is already started and going through the jobs that it will continue with the job list
            
            # run each job which is past it's deadline
            if now >= job.next_deadline:
                # calculate and set the next deadline
                elapsed = int((now - job.next_deadline) / job.period_s) + 1
                job.next_deadline += elapsed * job.period_s
                # set the job as a PSURunnable object
                runnable = PSURunnable(job, now)
                runnable.signals.failed.connect(lambda name, err: print(f"{name} failed: {err}"))
                self._pool.start(runnable)
