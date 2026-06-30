import time
import threading
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, QTimer, Signal, QRunnable, QThreadPool

@dataclass
class semaphore:
    semaphore_name: str = None
    semaphore_set: bool = False
    held_by: str = None  # job.name that currently holds it

@dataclass
class Job:
    # Structure the job with a list of semaphores and the function to be called upon
    name: str
    period_s: float
    func: callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    semaphores: list[semaphore] = field(default_factory=list)
    next_deadline: float = 0.0
    _acquired: list[semaphore] = field(default_factory=list, repr=False)  # internal

class JobSignals(QObject):
    # store the return signal in finished and failed, the failed part will only be read if executing the jobs func raises an excpetion
    finished = Signal(str, object)
    failed = Signal(str, str)

class PSURunnable(QRunnable):
    """
    Dataclass creating a job from a QRunnable object so they can be scheduled using QThreadPool
    """
    def __init__(self, job: Job, now: float, scheduler: "Scheduler"):
        super().__init__()
        self.job = job
        self.now = now
        self.scheduler = scheduler
        self.signals = JobSignals()
    # 
    def run(self):
        # attempt to run the job, if the job fails output message properly, this is 
        acquired = False
        # if available grab the semaphore and run with it, else skip the job
        try:
            acquired = self.scheduler._try_acquire(self.job)
            if not acquired:
                return  # semaphores not available; skip

            res = self.job.func(*self.job.args, **self.job.kwargs)
            self.signals.finished.emit(self.job.name, res)
        except Exception as e:
            # properly handles and outputs any exceptions raised by the job
            self.signals.failed.emit(self.job.name, repr(e))
        finally:
            # once the job is finished, release the semaphore
            if acquired:
                self.scheduler._release(self.job) # exit tick if stoped is set, this prevents an issue if the tick is already started and going through the jobs that it will continue with the job list

class Scheduler(QObject):
    def __init__(self, tick_ms=20, parent=None):
        super().__init__(parent)
        self._tick = QTimer(self)
        self._tick.setInterval(tick_ms)
        self._tick.timeout.connect(self._on_tick)

        self._jobs: list[Job] = []
        self._started = False
        self._stoped = False

        self._pool = QThreadPool.globalInstance()
        self._pool.setMaxThreadCount(8)
        # check to see if the semaphore is currently being read or written to, blocks several threads from accessing the same semaphore
        self._sem_lock = threading.Lock()
    # the * forces the following arguments to be called by name, preventing chaos, args stands for the positional arguments while kwargs stands for the keyword arguments
    def add_periodic(self, name, period_s, func, *, args=(), kwargs=None,
                      semaphores: list[semaphore] = None, start_immediately=False):
        """
        Add a periodic job to the list of jobs to be executed. You may also add a list of semaphores. 
        Semaphores prevent that two jobs with the same semaphore are run at the same time.
        Args:
        name(str): Name of the job (must be unique)
        period_s(float): Period at which the job is executed by the scheduler
        func: function which will run at the period defined by period_s
        args(): positional arguments to send to func
        kwargs(): keyword arguments to send to func
        semaphores: list of semaphores, prevents non thread safe processes from running at the same time
        start_immediately(bool): determines wheather the job should be started immediately or if it should wait until at least one period has passed.
        """
        if kwargs is None:
            kwargs = {}
        now = time.monotonic()
        next_deadline = now if start_immediately else (now + period_s)
        self._jobs.append(
            Job(
                name=name,
                period_s=period_s,
                func=func,
                args=args,
                kwargs=kwargs,
                semaphores=semaphores or [],
                next_deadline=next_deadline,
            )
        )

    def start_all(self):
        """
        Start the ticker of the sheduler and therefore start the scheduled jobs.
        """
        if self._started:
            return
        self._started = True
        self._tick.start()

    def stop(self):
        """
        Stop the ticker of the scheduler and therefore stop the scheduled jobs.
        """
        if self._stoped:
            return
        self._stoped = True
        self._tick.stop()

    def __del__(self):
        """
        when deleted stop the timer, otherwise the qt timer can remain active, which will trigger an exception when it's signal goes nowhere
        """
        try:
            self.stop()
        except:
            pass

    def _try_acquire(self, job: Job) -> bool:
        """
        Checks if the job that _on_tick is attempting to run has any semaphores
        """
        # checks if the semaphore is currently accessed by another thread and blocks the thread until the semaphore is not being read
        with self._sem_lock:
            # require ALL semaphores for this job to be free
            for sem in job.semaphores:
                if sem.semaphore_set:
                    return False

            # acquire all
            job._acquired = []
            for sem in job.semaphores:
                sem.semaphore_set = True
                sem.held_by = job.name
                job._acquired.append(sem)
            return True

    def _release(self, job: Job):
        # checks if the semaphore is currently accessed by another thread and blocks the thread until the semaphore is not being read
        with self._sem_lock:
            for sem in getattr(job, "_acquired", []) or []:
                sem.semaphore_set = False
                sem.held_by = None
            job._acquired = []

    def _on_tick(self):
        """
        Runs on every tick defined by tick_ms. Checks if the deadline of a job is due and if another job is holding a semaphore preventing the job from running.
        """
        now = time.monotonic()
        # exit tick if stoped is set, this prevents an issue if the tick is already started and going through the jobs that it will continue with the job list
        for job in self._jobs:
            if self._stoped:
                return

            # if any required semaphore is held, skip this job start
            any_held = False
            for sem in job.semaphores:
                if sem.semaphore_set:
                    any_held = True
                    break
            if any_held:
                continue

            if now >= job.next_deadline:
                elapsed = int((now - job.next_deadline) / job.period_s) + 1
                job.next_deadline += elapsed * job.period_s

                runnable = PSURunnable(job, now, self)
                runnable.signals.failed.connect(lambda name, err: print(f"{name} failed: {err}"))
                self._pool.start(runnable)
