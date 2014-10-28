#!/usr/bin/env python
import sys
import patch_socket
import timeit, cProfile

import credis

rds = credis.Connection()
rds.connect()

def bench_simple():
    'the operation for benchmark'
    rds.execute('SET', 'test', 100)

def bench_pipeline():
    rds.execute_pipeline(
            ('SET', 1, 1),
            ('INCR', 1),
            ('INCRBY', 1, 1),
            ('GET', 1),
        )

bench = bench_pipeline

# record once
patch_socket.run_with_recording(rds._sock, bench)

timeit.main(['-s', 'from __main__ import patch_socket, rds, bench',
            '-n', '10000', 'patch_socket.run_with_replay(rds._sock, bench)'])

if sys.version_info[0] >= 3:
    xrange = range

cProfile.run('for i in xrange(10000):patch_socket.run_with_replay(rds._sock, bench)',
             sort='time')

