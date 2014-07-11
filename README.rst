minimal redis client written in cython, 5X faster than redis-py.

Tutorial
========

execute command
---------------

.. code-block:: python

    >>> from credis import Connection
    >>> conn = Connection(host='127.0.0.1', port=6379)
    >>> conn.execute('set', 'test', 1)
    'OK'
    >>> conn.execute('get', 'test')
    '1'

execute pipelined commands
--------------------------

.. code-block:: python

    >>> commands = [('set', 'test%d'%i, i) for i in range(3)]
    >>> conn.execute_pipeline(*commands)
    ('OK', 'OK', 'OK')

connection pool for gevent
--------------------------

.. code-block:: python

    >>> from credis.geventpool import ResourcePool
    >>> pool = ResourcePool(32, Connection, host='127.0.0.1', port=6379)
    >>> with pool.ctx() as conn:
    ...     conn.execute('get', 'test')
    '1'
    >>> pool.execute('get', 'test')
    '1'
    >>> commands = [('get', 'test%d'%i) for i in range(3)]
    >>> pool.execute_pipeline(*commands)
    ('1', '2', '3')
