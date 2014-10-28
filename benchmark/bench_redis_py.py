#!/usr/bin/env python
import sys
import patch_socket
import timeit, cProfile

def run_with_recording(sock, func):
    sock.start_record()
    func()

def run_with_replay(sock, func):
    sock.start_replay()
    func()

import redis
from redis.connection import Connection

class DummyConnectionPool(object):
    def __init__(self):
        self.conn = Connection()

    def get_connection(self, *args, **kwargs):
        return self.conn

    def release(self, conn):
        pass

    def disconnect(self):
        pass

    def reinstantiate(self):
        pass

pool = DummyConnectionPool()
pool.conn.connect()
rds = redis.StrictRedis(connection_pool=pool)

def bench_simple():
    'the operation for benchmark'
    rds.set('test', 100)

def bench_pipeline():
    pipe = rds.pipeline()
    pipe.set(1, 1)
    pipe.incr(1)
    pipe.incrby(1, 1)
    pipe.get(1)
    pipe.execute()

bench = bench_pipeline

# record once
run_with_recording(pool.conn._sock, bench)

timeit.main(['-s', 'from __main__ import run_with_replay, pool, bench',
            '-n', '10000', 'run_with_replay(pool.conn._sock, bench)'])

if sys.version_info[0] >= 3:
    xrange = range

cProfile.run('for i in xrange(10000):run_with_replay(pool.conn._sock, bench)',
             sort='time')
