#!/usr/bin/env python
from credis import Connection

conn = Connection()

assert conn.execute(('SET', 1, 1)) == 'OK'
assert conn.execute(('GET', 1)) == '1'

# pipeline
pipe = []
pipe.append(('SET', 1, 2))
pipe.append(('GET', 1))
assert conn.execute_pipeline(pipe) == ('OK', '2')

pipe = [ ('SET', 1, 1),
         ('INCR', 1),
         ('INCRBY', 1, 1),
         ('GET', 1),
       ]
assert conn.execute_pipeline(pipe) == ('OK', 2, 3, '3')
