"""Small, process-local workload budget for a single-worker public demo."""
from collections import deque
from contextlib import contextmanager
import math
import threading
import time


class DemoBusy(Exception):
    def __init__(self, message, retry_after):
        super().__init__(message)
        self.retry_after = retry_after


class DemoBudget:
    """Reserve a request before model use; never refund failed model calls.

    This is a best-effort workload limit, not a provider billing cap. State is
    shared by threads, but resets on restart and is not shared across workers.
    """
    def __init__(self, hourly=30, daily=120, concurrent=2, clock=time.monotonic):
        self.hourly = hourly
        self.daily = daily
        self.concurrent = concurrent
        self.clock = clock
        self.started = deque()
        self.active = 0
        self.lock = threading.Lock()

    @contextmanager
    def slot(self):
        with self.lock:
            now = self.clock()
            while self.started and self.started[0] <= now - 86400:
                self.started.popleft()
            if self.active >= self.concurrent:
                raise DemoBusy('The public demo is busy. Please retry shortly.', 15)
            recent = [t for t in self.started if t > now - 3600]
            wait = 0
            if len(self.started) >= self.daily:
                wait = self.started[0] + 86400 - now
            if len(recent) >= self.hourly:
                wait = max(wait, recent[0] + 3600 - now)
            if wait > 0:
                raise DemoBusy('The public demo has reached its request budget. Please retry later.', max(1, math.ceil(wait)))
            self.started.append(now)
            self.active += 1
        try:
            yield
        finally:
            with self.lock:
                self.active -= 1
