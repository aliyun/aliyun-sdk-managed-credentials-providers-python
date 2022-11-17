# coding=utf-8
import threading


class RWLock(object):
    def __init__(self):
        self.rlock = threading.Lock()
        self.wlock = threading.Lock()
        self.reader = 0

    def write_acquire(self, blocking=None):
        return self.wlock.acquire(blocking)

    def write_release(self):
        self.wlock.release()

    def read_acquire(self):
        self.rlock.acquire()
        self.reader += 1
        if self.reader == 1:
            self.wlock.acquire()
        self.rlock.release()

    def read_release(self):
        self.rlock.acquire()
        self.reader -= 1
        if self.reader == 0 and self.wlock.locked():
            self.wlock.release()
        self.rlock.release()
