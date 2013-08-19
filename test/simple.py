#!/usr/bin/env python
from credis import Connection

conn = Connection()

conn.send_command(('SET', 1, 1))
assert conn.read_response() == 'OK'
conn.send_command(('GET', 1))
assert conn.read_response() == '1'

# pipeline
pipe = []
pipe.append(('SET', 1, 2))
pipe.append(('GET', 1))
conn.send_pipeline(pipe)
assert conn.read_n_response(len(pipe)) == ('OK', '2')

pipe = []
pipe.append( ('SET', 1, 1) )
pipe.append( ('INCR', 1) )
pipe.append( ('INCRBY', 1, 1) )
pipe.append( ('GET', 1) )
conn.send_pipeline(pipe)
assert conn.read_n_response(len(pipe)) == ('OK', 2, 3, '3')
