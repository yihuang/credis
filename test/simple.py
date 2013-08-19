#!/usr/bin/env python
from credis import Connection

conn = Connection(host=u'127.0.0.1')

conn.send_command(('SET', 1, 1))
assert conn.read_response() == 'OK'
conn.send_command(('GET', 1))
assert conn.read_response() == '1'

# pipeline
pipe = []
pipe.append(('SET', 1, 2))
pipe.append(('GET', 1))
conn.send_pipeline(pipe)
assert conn.read_response() == 'OK'
assert conn.read_response() == '2'
