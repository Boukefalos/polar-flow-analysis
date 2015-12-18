import time
import threading
import base64
import atexit
import sqlite3
import sys

class Persistent:
    pass

class SQLiteImplementation(Persistent):
    def __init__(self, database='limit-calls.db', session='-'):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute('DROP TABLE IF EXISTS per_second')
        self.cursor.execute('DROP TABLE IF EXISTS rate')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS per_second (id INTEGER PRIMARY KEY AUTOINCREMENT, target string, hash string, last_reset real, calls int, expire real)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS rate (id INTEGER PRIMARY KEY AUTOINCREMENT, target string, hash string, last_call real, expire real)')
        self.connection.commit()

    def __del__(self):
        self.cursor.execute('DELETE from per_second WHERE expire > {:f}'.format(time.time()))
        self.cursor.execute('DELETE from rate WHERE expire > {:f}'.format(time.time()))
        self.connection.commit()
        self.connection.close()

    def getCallsPerSecond(self, function, hash):
        target = function.__name__
        query = "SELECT last_reset, calls FROM per_second WHERE target = '{:s}' AND hash = '{:s}'".format(function.__name__, hash)
        self.cursor.execute(query);
        row = self.cursor.fetchone()
        if row is None:
            return ([0.0], [0])
        else:
            return ([row[0]], [row[1]])

    def setCallsPerSecond(self, function, hash, lastReset, calls, expire):
        query = "REPLACE INTO per_second (id, target, hash, last_reset, calls, expire) VALUES ((SELECT id FROM per_second WHERE target = '{0:s}' AND hash = '{1:s}'), '{0:s}', '{1:s}', {2:f}, {3:d}, {4:f})".format(function.__name__, hash, lastReset, calls, expire)
        self.cursor.execute(query);
        self.connection.commit()

    def getCallsRate(self, function, hash):
        target = function.__name__
        query = "SELECT last_call FROM rate WHERE target = '{:s}' AND hash = '{:s}'".format(function.__name__, hash)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row is None:
            return ([0.0])
        else:
            return ([row[0]])
  
    def setCallsRate(self, function, hash, lastCall, expire):
        query = "REPLACE INTO rate (id, target, hash, last_call, expire) VALUES ((SELECT id FROM rate WHERE target = '{0:s}' AND hash = '{1:s}'), '{0:s}', '{1:s}', {2:f}, {3:f})".format(function.__name__, hash, lastCall, expire)
        self.cursor.execute(query)
        self.connection.commit()

def limitCallsPerSecond(maxCalls, perSeconds, persistent, sleep=True):
    def decorate(function):
        lock = threading.RLock()
        hash = base64.b64encode('%d-%d-%s' % (maxCalls, perSeconds, sleep))
        (lastReset, calls) = persistent.getCallsPerSecond(function, hash)
        def store(expire):
            persistent.setCallsPerSecond(function, hash, lastReset[0], calls[0], expire)
        def reset(time=time.time()):
            lastReset[0] = time
            calls[0] = maxCalls
            store(time + perSeconds)
        def wrapper(*args, **kargs):
            lock.acquire()
            now = time.time()
            sinceLastReset = now - lastReset[0]
            if sinceLastReset > perSeconds:
                reset(now)
            else:
                calls[0] = calls[0] - 1
                store(now + perSeconds)
            outOfCalls = calls[0] < 1
            if outOfCalls and sleep:
                leftToWait = perSeconds - sinceLastReset
                time.sleep(leftToWait)
                reset()
                leftToWait = False
            lock.release()
            if outOfCalls is False:
                return function(*args, **kargs)
        return wrapper
    return decorate

def limitCallsRate(maxPerSecond, perSecond, persistent, sleep=True):
    def decorate(function):        
        lock = threading.RLock()
        minInterval = perSecond / float(maxPerSecond)
        hash = base64.b64encode(('%d-%d-%s' % (maxPerSecond, perSecond, sleep)).encode()).decode()
        print(hash)
        lastCall = persistent.getCallsRate(function, hash)
        def store(expire):
            persistent.setCallsRate(function, hash, lastCall[0], expire)
        def wrapper(*args, **kargs):
            lock.acquire()
            elapsed = time.time() - lastCall[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                if sleep:
                    time.sleep(leftToWait)                        
                else:
                    lock.release()
                    return
            try:
                toReturn = function(*args, **kargs)
            finally:
                lastCall[0] = time.time()
                store(lastCall[0] + minInterval)
                lock.release()
            return toReturn
        return wrapper
    return decorate

if __name__ == "__main__":
    persistent = SQLiteImplementation()
    @limitCallsPerSecond(3, 4, persistent)
    @limitCallsRate(2, 1, persistent)

    def PrintNumber(num):
        print("%s: %d" % (time.time(), num))
        time.sleep(0.01)
        return True

    i = 1
    while i < 10000:
        if not PrintNumber(i):
            time.sleep(0.1)
        i = i + 1