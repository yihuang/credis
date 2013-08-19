import gevent
from credis.geventpool import Pool

counter = 0
def get_resource():
    global counter
    counter += 1
    return counter

def worker(pool):
    res = pool.acquire()
    gevent.sleep(0.05)
    pool.release(res)

pool = Pool(10, get_resource)
threads = [gevent.spawn(worker, pool) for i in xrange(10000)]
gevent.joinall(threads)
assert pool.alloc_count <= pool.max_count
assert pool.used_count == 0
