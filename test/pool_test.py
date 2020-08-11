#!/usr/bin/env python
import gevent
import random
from credis.geventpool import ResourcePool
import unittest
import typing


class CRedisException(Exception):
    pass


class TestPool(unittest.TestCase):
    def setUp(self) -> None:
        self.counter = 0

    def test_pool(self) -> None:
        pool = ResourcePool(10, self.get_resource)
        threads = [gevent.spawn(self.random_worker(), pool) for _ in range(1000)]
        gevent.joinall(threads)
        assert pool.alloc_count <= pool.max_count
        assert pool.used_count == 0
        assert self.counter == 10

    def random_worker(self) -> typing.Callable:
        return random.choice(
            [
                self.worker_normal,
                self.worker_exception,
                self.worker_using_with,
                self.worker_using_with2,
            ]
        )

    def worker_normal(self, pool):
        res = pool.acquire()
        gevent.sleep(0.05)
        pool.release(res)

    def worker_exception(self, pool):
        res = pool.acquire()
        try:
            gevent.sleep(0.05)
            raise CRedisException("bad worker")
        except CRedisException:
            pass
        finally:
            pool.release(res)

    def worker_using_with(self, pool):
        try:
            with pool.ctx() as res:
                gevent.sleep(0.05)
                raise CRedisException("bad worker1")
        except CRedisException:
            pass

    def worker_using_with2(self, pool):
        try:
            with pool.ctx() as res:
                gevent.sleep(0.05)
                raise CRedisException("bad worker2")
        except CRedisException:
            pass

    def get_resource(self):
        self.counter += 1
        return self.counter
