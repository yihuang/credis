#!/usr/bin/env python
import gevent
import random
from credis.geventpool import ResourcePool

counter = 0
def get_resource():
    global counter
    counter += 1
    return counter

class TestException(Exception):
    pass

def worker_normal(pool):
    res = pool.acquire()
    gevent.sleep(0.05)
    pool.release(res)

def worker_exception(pool):
    res = pool.acquire()
    try:
        gevent.sleep(0.05)
        raise TestException('bad worker')
    except TestException:
        pass
    finally:
        pool.release(res)

def worker_using_with(pool):
    try:
        with pool.ctx() as res:
            gevent.sleep(0.05)
            raise TestException('bad worker1')
    except TestException:
        pass

def worker_using_with2(pool):
    try:
        with pool.ctx() as res:
            gevent.sleep(0.05)
            raise TestException('bad worker2')
    except TestException:
        pass

def random_worker():
    return random.choice([worker_normal, worker_exception, worker_using_with, worker_using_with2])

pool = ResourcePool(10, get_resource)
threads = [gevent.spawn(random_worker(), pool) for i in xrange(1000)]
gevent.joinall(threads)
assert pool.alloc_count <= pool.max_count
assert pool.used_count == 0
assert counter == 10
