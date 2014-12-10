from gevent.event import AsyncResult
from contextlib import contextmanager

cdef class ResourcePool:
    '''
    simple pool, used for gevent, there is not true concurrency.
    '''
    cdef public list _pool
    cdef public object ctor
    cdef public tuple args
    cdef public dict kwargs
    cdef public str name

    cdef public int max_count
    cdef public int alloc_count
    cdef public int used_count

    cdef list _waiters

    def __cinit__(self, max_count, ctor, *args, **kwargs):
        self.ctor = ctor
        self.args = args
        self.name = kwargs.pop('name', None)
        self.kwargs = kwargs

        self.max_count = max_count
        self.alloc_count = 0
        self.used_count = 0

        self._pool = []
        self._waiters = []

    cpdef acquire(self):
        try:
            res = self._pool.pop()
        except IndexError:
            if self.alloc_count >= self.max_count:
                evt = AsyncResult()
                self._waiters.append(evt)
                return evt.get()

            # allocate new resource
            res = self.ctor(*self.args, **self.kwargs)
            self.alloc_count += 1
            self.used_count += 1
        else:
            self.used_count += 1
        assert self.alloc_count - self.used_count == len(self._pool), 'impossible[1]'
        assert self.used_count <= self.alloc_count, 'impossible[2]'
        assert res is not None, 'impossible[4]'
        return res

    cpdef release(self, item):
        assert item is not None, 'invalid item'
        if len(self._waiters) > 0:
            self._waiters.pop().set(item)
        else:
            self.used_count -= 1
            self._pool.append(item)
        assert self.used_count >= 0, 'impossible[3]'

    def ctx(self):
        return pool_context(self)

    def execute(self, *args):
        with self.ctx() as conn:
            return conn.execute(*args)

    def execute_pipeline(self, *args):
        with self.ctx() as conn:
            return conn.execute_pipeline(*args)

@contextmanager
def pool_context(pool):
    res = pool.acquire()
    try:
        yield res
    finally:
        pool.release(res)
