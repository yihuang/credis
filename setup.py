# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['credis']

package_data = \
{'': ['*']}

install_requires = \
['hiredis>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'credis',
    'version': '2.0.1',
    'description': 'high performance redis client implemented with cython',
    'long_description': "minimal redis client written in cython, 5X faster than redis-py.\n\nTutorial\n========\n\nexecute command\n---------------\n\n.. code-block:: python\n\n    >>> from credis import Connection\n    >>> conn = Connection(host='127.0.0.1', port=6379)\n    >>> conn.execute('set', 'test', 1)\n    'OK'\n    >>> conn.execute('get', 'test')\n    '1'\n\nexecute pipelined commands\n--------------------------\n\n.. code-block:: python\n\n    >>> commands = [('set', 'test%d'%i, i) for i in range(3)]\n    >>> conn.execute_pipeline(*commands)\n    ('OK', 'OK', 'OK')\n\nconnection pool for gevent\n--------------------------\n\n.. code-block:: python\n\n    >>> from credis.geventpool import ResourcePool\n    >>> pool = ResourcePool(32, Connection, host='127.0.0.1', port=6379)\n    >>> with pool.ctx() as conn:\n    ...     conn.execute('get', 'test')\n    '1'\n    >>> pool.execute('get', 'test')\n    '1'\n    >>> commands = [('get', 'test%d'%i) for i in range(3)]\n    >>> pool.execute_pipeline(*commands)\n    ('1', '2', '3')\n",
    'author': 'yihuang',
    'author_email': 'yi.codeplayer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yihuang/credis',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
