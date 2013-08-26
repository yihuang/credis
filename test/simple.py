#!/usr/bin/env python
from credis import Connection

conn = Connection()

assert conn.execute('SET', 1, 1) == 'OK'
assert conn.execute('GET', 1) == '1'

# pipeline
assert conn.execute_pipeline(
        ('SET', 1, 2),
        ('GET', 1),
    ) == ('OK', '2')

assert conn.execute_pipeline(
        ('SET', 1, 1),
        ('INCR', 1),
        ('INCRBY', 1, 1),
        ('GET', 1),
    ) == ('OK', 2, 3, '3')
