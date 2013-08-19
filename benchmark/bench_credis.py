#!/usr/bin/env python
import patch_socket
import timeit, cProfile

import credis

rds = credis.Connection()
rds.connect()

def bench_simple():
    'the operation for benchmark'
    rds.send_command(('SET', 'test', 100))
    assert rds.read_response()=='OK'

def bench_pipeline():
    pipe = []
    pipe.append( ('SET', 1, 1) )
    pipe.append( ('INCR', 1) )
    pipe.append( ('INCRBY', 1, 1) )
    pipe.append( ('GET', 1) )
    rds.send_pipeline(pipe)
    assert rds.read_n_response(len(pipe)) == ('OK', 2, 3, '3')

bench = bench_pipeline

# record once
patch_socket.run_with_recording(rds._sock, bench)

timeit.main(['-s', 'from __main__ import patch_socket, rds, bench',
            '-n', '10000', 'patch_socket.run_with_replay(rds._sock, bench)'])

cProfile.run('for i in xrange(10000):patch_socket.run_with_replay(rds._sock, bench)',
             sort='time')

