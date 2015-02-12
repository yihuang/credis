import socket
import datetime
import time
import warnings
import base

RedisProtocolError = base.RedisProtocolError
ConnectionError = base.ConnectionError


def list_or_args(keys, args):
    # returns a single list combining keys and args
    try:
        i = iter(keys)
        # a string can be iterated, but indicates
        # keys wasn't passed as a list
        if isinstance(keys, basestring):
            keys = [keys]
    except TypeError:
        keys = [keys]
    if args:
        keys.extend(args)
    return keys


class CRedis(base.Connection):
    """A simple wrapper for credis client
    """

    #### SERVER INFORMATION ####
    def bgrewriteaof(self):
        "Tell the Redis server to rewrite the AOF file from data in memory."
        return self.execute('BGREWRITEAOF')

    def bgsave(self):
        """
        Tell the Redis server to save its data to disk.  Unlike save(),
        this method is asynchronous and returns immediately.
        """
        return self.execute('BGSAVE')

    def config_get(self, pattern="*"):
        """Return a dictionary of configuration based on the ``pattern``"""
        return self.execute('CONFIG', 'GET', pattern)

    def config_set(self, name, value):
        """Set config item ``name`` with ``value``"""
        return self.execute('CONFIG', 'SET', name, value)

    def dbsize(self):
        """Returns the number of keys in the current database"""
        return self.execute('DBSIZE')

    def delete(self, *names):
        """Delete one or more keys specified by ``names``"""
        return self.execute('DEL', *names)

    def flushall(self):
        """Delete all keys in all databases on the current host"""
        return self.execute('FLUSHALL')

    def flushdb(self):
        """Delete all keys in the current database"""
        return self.execute('FLUSHDB')

    def info(self):
        """Returns a dictionary containing information about the Redis server"""
        return self.execute('INFO')

    def lastsave(self):
        """
        Return a Python datetime object representing the last time the
        Redis database was saved to disk
        """
        return self.execute('LASTSAVE')

    def ping(self):
        """Ping the Redis server"""
        return self.execute('PING')

    def save(self):
        """
        Tell the Redis server to save its data to disk,
        blocking until the save is complete
        """
        return self.execute('SAVE')

    def select(self, index):
        """
        Select the DB having the specified zero-based numeric index.
        """
        return self.execute('SELECT', index)

    def shutdown(self):
        """Shutdown the server"""
        try:
            self.execute('SHUTDOWN')
        except socket.error:
            # a socket.error here is expected
            return
        raise ConnectionError("SHUTDOWN seems to have failed.")

    def slaveof(self, host=None, port=None):
        """
        Set the server to be a replicated slave of the instance identified
        by the ``host`` and ``port``. If called without arguements, the
        instance is promoted to a master instead.
        """
        if host is None and port is None:
            return self.execute("SLAVEOF", "NO", "ONE")
        return self.execute("SLAVEOF", host, port)

    #### BASIC KEY COMMANDS ####
    def append(self, key, value):
        """
        Appends the string ``value`` to the value at ``key``. If ``key``
        doesn't already exist, create it with a value of ``value``.
        Returns the new length of the value at ``key``.
        """
        return self.execute('APPEND', key, value)

    def decr(self, name, amount=1):
        """
        Decrements the value of ``key`` by ``amount``.  If no key exists,
        the value will be initialized as 0 - ``amount``
        """
        return self.execute('DECRBY', name, amount)

    def exists(self, name):
        """Returns a boolean indicating whether key ``name`` exists"""
        return self.execute('EXISTS', name)

    def expire(self, name, time):
        """Set an expire flag on key ``name`` for ``time`` seconds"""
        return self.execute('EXPIRE', name, time)

    def expireat(self, name, when):
        """
        Set an expire flag on key ``name``. ``when`` can be represented
        as an integer indicating unix time or a Python datetime object.
        """
        if isinstance(when, datetime.datetime):
            when = int(time.mktime(when.timetuple()))
        return self.execute('EXPIREAT', name, when)

    def get(self, name):
        """
        Return the value at key ``name``, or None if the key doesn't exist
        """
        return self.execute('GET', name)

    def getbit(self, name, offset):
        """Returns a boolean indicating the value of ``offset`` in ``name``"""
        return self.execute('GETBIT', name, offset)

    def getset(self, name, value):
        """
        Set the value at key ``name`` to ``value`` if key doesn't exist
        Return the value at key ``name`` atomically
        """
        return self.execute('GETSET', name, value)

    def incr(self, name, amount=1):
        """
        Increments the value of ``key`` by ``amount``.  If no key exists,
        the value will be initialized as ``amount``
        """
        return self.execute('INCRBY', name, amount)

    def keys(self, pattern='*'):
        """Returns a list of keys matching ``pattern``"""
        return self.execute('KEYS', pattern)

    def mget(self, keys, *args):
        """
        Returns a list of values ordered identically to ``keys``
        """
        keys = list_or_args(keys, args)
        return self.execute('MGET', *keys)

    def mset(self, mapping):
        """Sets each key in the ``mapping`` dict to its corresponding value"""
        items = []
        for pair in mapping.iteritems():
            items.extend(pair)
        return self.execute('MSET', *items)

    def msetnx(self, mapping):
        """
        Sets each key in the ``mapping`` dict to its corresponding value if
        none of the keys are already set
        """
        items = []
        for pair in mapping.iteritems():
            items.extend(pair)
        return self.execute('MSETNX', *items)

    def move(self, name, db):
        """Moves the key ``name`` to a different Redis database ``db``"""
        return self.execute('MOVE', name, db)

    def persist(self, name):
        """Removes an expiration on ``name``"""
        return self.execute('PERSIST', name)

    def randomkey(self):
        """Returns the name of a random key"""
        return self.execute('RANDOMKEY')

    def rename(self, src, dst):
        """
        Rename key ``src`` to ``dst``
        """
        return self.execute('RENAME', src, dst)

    def renamenx(self, src, dst):
        """Rename key ``src`` to ``dst`` if ``dst`` doesn't already exist"""
        return self.execute('RENAMENX', src, dst)

    def set(self, name, value):
        """Set the value at key ``name`` to ``value``"""
        return self.execute('SET', name, value)

    def setbit(self, name, offset, value):
        """
        Flag the ``offset`` in ``name`` as ``value``. Returns a boolean
        indicating the previous value of ``offset``.
        """
        value = value and 1 or 0
        return self.execute('SETBIT', name, offset, value)

    def setex(self, name, value, time):
        """
        Set the value of key ``name`` to ``value``
        that expires in ``time`` seconds
        """
        return self.execute('SETEX', name, time, value)

    def setnx(self, name, value):
        """Set the value of key ``name`` to ``value`` if key doesn't exist"""
        return self.execute('SETNX', name, value)

    def setrange(self, name, offset, value):
        """
        Overwrite bytes in the value of ``name`` starting at ``offset`` with
        ``value``. If ``offset`` plus the length of ``value`` exceeds the
        length of the original value, the new value will be larger than before.
        If ``offset`` exceeds the length of the original value, null bytes
        will be used to pad between the end of the previous value and the start
        of what's being injected.

        Returns the length of the new string.
        """
        return self.execute('SETRANGE', name, offset, value)

    def strlen(self, name):
        """Return the number of bytes stored in the value of ``name``"""
        return self.execute('STRLEN', name)

    def substr(self, name, start, end=-1):
        """
        Return a substring of the string at key ``name``. ``start`` and ``end``
        are 0-based integers specifying the portion of the string to return.
        """
        return self.execute('SUBSTR', name, start, end)

    def ttl(self, name):
        """Returns the number of seconds until the key ``name`` will expire"""
        return self.execute('TTL', name)

    def type(self, name):
        """Returns the type of key ``name``"""
        return self.execute('TYPE', name)

    def watch(self, *names):
        """
        Watches the values at keys ``names``, or None if the key doesn't exist
        """
        warnings.warn(DeprecationWarning('Call WATCH from a Pipeline object'))

    def unwatch(self):
        """
        Unwatches the value at key ``name``, or None of the key doesn't exist
        """
        warnings.warn(DeprecationWarning('Call UNWATCH from a Pipeline object'))

    #### LIST COMMANDS ####
    def blpop(self, keys, timeout=0):
        """
        LPOP a value off of the first non-empty list
        named in the ``keys`` list.

        If none of the lists in ``keys`` has a value to LPOP, then block
        for ``timeout`` seconds, or until a value gets pushed on to one
        of the lists.

        If timeout is 0, then block indefinitely.
        """
        if timeout is None:
            timeout = 0
        if isinstance(keys, basestring):
            keys = [keys]
        else:
            keys = list(keys)
        keys.append(timeout)
        return self.execute('BLPOP', *keys)

    def brpop(self, keys, timeout=0):
        """
        RPOP a value off of the first non-empty list
        named in the ``keys`` list.

        If none of the lists in ``keys`` has a value to LPOP, then block
        for ``timeout`` seconds, or until a value gets pushed on to one
        of the lists.

        If timeout is 0, then block indefinitely.
        """
        if timeout is None:
            timeout = 0
        if isinstance(keys, basestring):
            keys = [keys]
        else:
            keys = list(keys)
        keys.append(timeout)
        return self.execute('BRPOP', *keys)

    def brpoplpush(self, src, dst, timeout=0):
        """
        Pop a value off the tail of ``src``, push it on the head of ``dst``
        and then return it.

        This command blocks until a value is in ``src`` or until ``timeout``
        seconds elapse, whichever is first. A ``timeout`` value of 0 blocks
        forever.
        """
        if timeout is None:
            timeout = 0
        return self.execute('BRPOPLPUSH', src, dst, timeout)

    def lindex(self, name, index):
        """
        Return the item from list ``name`` at position ``index``

        Negative indexes are supported and will return an item at the
        end of the list
        """
        return self.execute('LINDEX', name, index)

    def linsert(self, name, where, refvalue, value):
        """
        Insert ``value`` in list ``name`` either immediately before or after
        [``where``] ``refvalue``

        Returns the new length of the list on success or -1 if ``refvalue``
        is not in the list.
        """
        return self.execute('LINSERT', name, where, refvalue, value)

    def llen(self, name):
        """Return the length of the list ``name``"""
        return self.execute('LLEN', name)

    def lpop(self, name):
        """Remove and return the first item of the list ``name``"""
        return self.execute('LPOP', name)

    def lpush(self, name, *values):
        """Push ``values`` onto the head of the list ``name``"""
        return self.execute('LPUSH', name, *values)

    def lpushx(self, name, value):
        """
        Push ``value`` onto the head of the list ``name`` if ``name`` exists
        """
        return self.execute('LPUSHX', name, value)

    def lrange(self, name, start, end):
        """
        Return a slice of the list ``name`` between
        position ``start`` and ``end``

        ``start`` and ``end`` can be negative numbers just like
        Python slicing notation
        """
        return self.execute('LRANGE', name, start, end)

    def lrem(self, name, value, num=0):
        """
        Remove the first ``num`` occurrences of ``value`` from list ``name``

        If ``num`` is 0, then all occurrences will be removed
        """
        return self.execute('LREM', name, num, value)

    def lset(self, name, index, value):
        """Set ``position`` of list ``name`` to ``value``"""
        return self.execute('LSET', name, index, value)

    def ltrim(self, name, start, end):
        """
        Trim the list ``name``, removing all values not within the slice
        between ``start`` and ``end``

        ``start`` and ``end`` can be negative numbers just like
        Python slicing notation
        """
        return self.execute('LTRIM', name, start, end)

    def rpop(self, name):
        """Remove and return the last item of the list ``name``"""
        return self.execute('RPOP', name)

    def rpoplpush(self, src, dst):
        """
        RPOP a value off of the ``src`` list and atomically LPUSH it
        on to the ``dst`` list.  Returns the value.
        """
        return self.execute('RPOPLPUSH', src, dst)

    def rpush(self, name, *values):
        """Push ``values`` onto the tail of the list ``name``"""
        return self.execute('RPUSH', name, *values)

    def rpushx(self, name, value):
        """
        Push ``value`` onto the tail of the list ``name`` if ``name`` exists
        """
        return self.execute('RPUSHX', name, value)

    def sort(self, name, start=None, num=None, by=None, get=None,
             desc=False, alpha=False, store=None):
        """
        Sort and return the list, set or sorted set at ``name``.

        ``start`` and ``num`` allow for paging through the sorted data

        ``by`` allows using an external key to weight and sort the items.
            Use an "*" to indicate where in the key the item value is located

        ``get`` allows for returning items from external keys rather than the
            sorted data itself.  Use an "*" to indicate where int he key
            the item value is located

        ``desc`` allows for reversing the sort

        ``alpha`` allows for sorting lexicographically rather than numerically

        ``store`` allows for storing the result of the sort into
            the key ``store``
        """
        if (start is not None and num is None) or \
                (num is not None and start is None):
            raise RedisProtocolError("``start`` and ``num`` must both be specified")

        pieces = [name]
        if by is not None:
            pieces.append('BY')
            pieces.append(by)
        if start is not None and num is not None:
            pieces.append('LIMIT')
            pieces.append(start)
            pieces.append(num)
        if get is not None:
            # If get is a string assume we want to get a single value.
            # Otherwise assume it's an interable and we want to get multiple
            # values. We can't just iterate blindly because strings are
            # iterable.
            if isinstance(get, basestring):
                pieces.append('GET')
                pieces.append(get)
            else:
                for g in get:
                    pieces.append('GET')
                    pieces.append(g)
        if desc:
            pieces.append('DESC')
        if alpha:
            pieces.append('ALPHA')
        if store is not None:
            pieces.append('STORE')
            pieces.append(store)
        return self.execute('SORT', *pieces)


    #### SET COMMANDS ####
    def sadd(self, name, *values):
        """Add ``value(s)`` to set ``name``"""
        return self.execute('SADD', name, *values)

    def scard(self, name):
        """Return the number of elements in set ``name``"""
        return self.execute('SCARD', name)

    def sdiff(self, keys, *args):
        """Return the difference of sets specified by ``keys``"""
        keys = list_or_args(keys, args)
        return self.execute('SDIFF', *keys)

    def sdiffstore(self, dest, keys, *args):
        """
        Store the difference of sets specified by ``keys`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        keys = list_or_args(keys, args)
        return self.execute('SDIFFSTORE', dest, *keys)

    def sinter(self, keys, *args):
        """Return the intersection of sets specified by ``keys``"""
        keys = list_or_args(keys, args)
        return self.execute('SINTER', *keys)

    def sinterstore(self, dest, keys, *args):
        """
        Store the intersection of sets specified by ``keys`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        keys = list_or_args(keys, args)
        return self.execute('SINTERSTORE', dest, *keys)

    def sismember(self, name, value):
        """
        Return a boolean indicating if ``value`` is a member of set ``name``
        """
        return self.execute('SISMEMBER', name, value)

    def smembers(self, name):
        """Return all members of the set ``name``"""
        return self.execute('SMEMBERS', name)

    def smove(self, src, dst, value):
        """Move ``value`` from set ``src`` to set ``dst`` atomically"""
        return self.execute('SMOVE', src, dst, value)

    def spop(self, name):
        """Remove and return a random member of set ``name``"""
        return self.execute('SPOP', name)

    def srandmember(self, name):
        """Return a random member of set ``name``"""
        return self.execute('SRANDMEMBER', name)

    def srem(self, name, *values):
        """Remove ``values`` from set ``name``"""
        return self.execute('SREM', name, *values)

    def sunion(self, keys, *args):
        """Return the union of sets specifiued by ``keys``"""
        keys = list_or_args(keys, args)
        return self.execute('SUNION', *keys)

    def sunionstore(self, dest, keys, *args):
        """
        Store the union of sets specified by ``keys`` into a new
        set named ``dest``.  Returns the number of keys in the new set.
        """
        keys = list_or_args(keys, args)
        return self.execute('SUNIONSTORE', dest, *keys)


    #### SORTED SET COMMANDS ####
    def zadd(self, name, value=None, score=None, **pairs):
        """
        For each kwarg in ``pairs``, add that item and it's score to the
        sorted set ``name``.

        The ``value`` and ``score`` arguments are deprecated.
        """
        all_pairs = []
        if value is not None or score is not None:
            if value is None or score is None:
                raise RedisProtocolError("Both 'value' and 'score' must be specified " \
                                         "to ZADD")
            warnings.warn(DeprecationWarning(
                "Passing 'value' and 'score' has been deprecated. " \
                "Please pass via kwargs instead."))
            all_pairs.append(score)
            all_pairs.append(value)
        for pair in pairs.iteritems():
            all_pairs.append(pair[1])
            all_pairs.append(pair[0])
        return self.execute('ZADD', name, *all_pairs)

    def zcard(self, name):
        """Return the number of elements in the sorted set ``name``"""
        return self.execute('ZCARD', name)

    def zcount(self, name, min, max):
        return self.execute('ZCOUNT', name, min, max)

    def zincrby(self, name, value, amount=1):
        """
        Increment the score of ``value`` in sorted set ``name`` by ``amount``
        """
        return self.execute('ZINCRBY', name, amount, value)

    def zinterstore(self, dest, keys, aggregate=None):
        """
        Intersect multiple sorted sets specified by ``keys`` into
        a new sorted set, ``dest``. Scores in the destination will be
        aggregated based on the ``aggregate``, or SUM if none is provided.
        """
        return self._zaggregate('ZINTERSTORE', dest, keys, aggregate)

    def zrange(self, name, start, end, desc=False, withscores=False,
               score_cast_func=float):
        """
        Return a range of values from sorted set ``name`` between
        ``start`` and ``end`` sorted in ascending order.

        ``start`` and ``end`` can be negative, indicating the end of the range.

        ``desc`` a boolean indicating whether to sort the results descendingly

        ``withscores`` indicates to return the scores along with the values.
        The return type is a list of (value, score) pairs

        ``score_cast_func`` a callable used to cast the score return value
        """
        if desc:
            return self.zrevrange(name, start, end, withscores)
        pieces = ['ZRANGE', name, start, end]
        if withscores:
            pieces.append('withscores')
        options = {'withscores': withscores, 'score_cast_func': score_cast_func}
        return self.execute(*pieces, **options)

    def zrangebyscore(self, name, min, max,
                      start=None, num=None, withscores=False, score_cast_func=float):
        """
        Return a range of values from the sorted set ``name`` with scores
        between ``min`` and ``max``.

        If ``start`` and ``num`` are specified, then return a slice
        of the range.

        ``withscores`` indicates to return the scores along with the values.
        The return type is a list of (value, score) pairs

        `score_cast_func`` a callable used to cast the score return value
        """
        if (start is not None and num is None) or \
                (num is not None and start is None):
            raise RedisProtocolError("``start`` and ``num`` must both be specified")
        pieces = ['ZRANGEBYSCORE', name, min, max]
        if start is not None and num is not None:
            pieces.extend(['LIMIT', start, num])
        if withscores:
            pieces.append('withscores')
        options = {'withscores': withscores, 'score_cast_func': score_cast_func}
        return self.execute(*pieces, **options)

    def zrank(self, name, value):
        """
        Returns a 0-based value indicating the rank of ``value`` in sorted set
        ``name``
        """
        return self.execute('ZRANK', name, value)

    def zrem(self, name, *values):
        """Remove member ``values`` from sorted set ``name``"""
        return self.execute('ZREM', name, *values)

    def zremrangebyrank(self, name, min, max):
        """
        Remove all elements in the sorted set ``name`` with ranks between
        ``min`` and ``max``. Values are 0-based, ordered from smallest score
        to largest. Values can be negative indicating the highest scores.
        Returns the number of elements removed
        """
        return self.execute('ZREMRANGEBYRANK', name, min, max)

    def zremrangebyscore(self, name, min, max):
        """
        Remove all elements in the sorted set ``name`` with scores
        between ``min`` and ``max``. Returns the number of elements removed.
        """
        return self.execute('ZREMRANGEBYSCORE', name, min, max)

    def zrevrange(self, name, start, num, withscores=False,
                  score_cast_func=float):
        """
        Return a range of values from sorted set ``name`` between
        ``start`` and ``num`` sorted in descending order.

        ``start`` and ``num`` can be negative, indicating the end of the range.

        ``withscores`` indicates to return the scores along with the values
        The return type is a list of (value, score) pairs

        ``score_cast_func`` a callable used to cast the score return value
        """
        pieces = ['ZREVRANGE', name, start, num]
        if withscores:
            pieces.append('withscores')
        options = {'withscores': withscores, 'score_cast_func': score_cast_func}
        return self.execute(*pieces, **options)

    def zrevrangebyscore(self, name, max, min,
                         start=None, num=None, withscores=False, score_cast_func=float):
        """
        Return a range of values from the sorted set ``name`` with scores
        between ``min`` and ``max`` in descending order.

        If ``start`` and ``num`` are specified, then return a slice
        of the range.

        ``withscores`` indicates to return the scores along with the values.
        The return type is a list of (value, score) pairs

        ``score_cast_func`` a callable used to cast the score return value
        """
        if (start is not None and num is None) or \
                (num is not None and start is None):
            raise RedisProtocolError("``start`` and ``num`` must both be specified")
        pieces = ['ZREVRANGEBYSCORE', name, max, min]
        if start is not None and num is not None:
            pieces.extend(['LIMIT', start, num])
        if withscores:
            pieces.append('withscores')
        options = {'withscores': withscores, 'score_cast_func': score_cast_func}
        return self.execute(*pieces, **options)

    def zrevrank(self, name, value):
        """
        Returns a 0-based value indicating the descending rank of
        ``value`` in sorted set ``name``
        """
        return self.execute('ZREVRANK', name, value)

    def zscore(self, name, value):
        """Return the score of element ``value`` in sorted set ``name``"""
        return self.execute('ZSCORE', name, value)

    def zunionstore(self, dest, keys, aggregate=None):
        """
        Union multiple sorted sets specified by ``keys`` into
        a new sorted set, ``dest``. Scores in the destination will be
        aggregated based on the ``aggregate``, or SUM if none is provided.
        """
        return self._zaggregate('ZUNIONSTORE', dest, keys, aggregate)

    def _zaggregate(self, command, dest, keys, aggregate=None):
        pieces = [command, dest, len(keys)]
        if isinstance(keys, dict):
            keys, weights = keys.keys(), keys.values()
        else:
            weights = None
        pieces.extend(keys)
        if weights:
            pieces.append('WEIGHTS')
            pieces.extend(weights)
        if aggregate:
            pieces.append('AGGREGATE')
            pieces.append(aggregate)
        return self.execute(*pieces)

    #### HASH COMMANDS ####
    def hdel(self, name, *keys):
        """Delete ``keys`` from hash ``name``"""
        return self.execute('HDEL', name, *keys)

    def hexists(self, name, key):
        """
        Returns a boolean indicating if ``key`` exists within hash ``name``
        """
        return self.execute('HEXISTS', name, key)

    def hget(self, name, key):
        """Return the value of ``key`` within the hash ``name``"""
        return self.execute('HGET', name, key)

    def hgetall(self, name):
        """Return a Python dict of the hash's name/value pairs"""
        return self.execute('HGETALL', name)

    def hincrby(self, name, key, amount=1):
        """Increment the value of ``key`` in hash ``name`` by ``amount``"""
        return self.execute('HINCRBY', name, key, amount)

    def hkeys(self, name):
        """Return the list of keys within hash ``name``"""
        return self.execute('HKEYS', name)

    def hlen(self, name):
        """Return the number of elements in hash ``name``"""
        return self.execute('HLEN', name)

    def hset(self, name, key, value):
        """
        Set ``key`` to ``value`` within hash ``name``
        Returns 1 if HSET created a new field, otherwise 0
        """
        return self.execute('HSET', name, key, value)

    def hsetnx(self, name, key, value):
        """
        Set ``key`` to ``value`` within hash ``name`` if ``key`` does not
        exist.  Returns 1 if HSETNX created a field, otherwise 0.
        """
        return self.execute("HSETNX", name, key, value)

    def hmset(self, name, mapping):
        """
        Sets each key in the ``mapping`` dict to its corresponding value
        in the hash ``name``
        """
        if not mapping:
            raise RedisProtocolError("'hmset' with 'mapping' of length 0")
        items = []
        for pair in mapping.iteritems():
            items.extend(pair)
        return self.execute('HMSET', name, *items)

    def hmget(self, name, keys):
        """Returns a list of values ordered identically to ``keys``"""
        return self.execute('HMGET', name, *keys)

    def hvals(self, name):
        """Return the list of values within hash ``name``"""
        return self.execute('HVALS', name)

    def publish(self, channel, message):
        """
        Publish ``message`` on ``channel``.
        Returns the number of subscribers the message was delivered to.
        """
        return self.execute('PUBLISH', channel, message)

    #### PUB/SUB COMMANDS ####
    def psubscribe(self, patterns):
        """Subscribe to all channels matching any pattern in ``patterns``"""
        pass

    def punsubscribe(self, patterns=[]):
        """
        Unsubscribe from any channel matching any pattern in ``patterns``.
        """
        if isinstance(patterns, basestring):
            patterns = [patterns]
        return self.execute('PUNSUBSCRIBE', *patterns)

    def subscribe(self, patterns):
        """Subscribe to all channels matching any pattern in ``patterns``"""
        pass

    def unsubscribe(self, patterns=[]):
        """
        Unsubscribe from any channel matching any pattern in ``patterns``.
        """
        if isinstance(patterns, basestring):
            patterns = [patterns]
        return self.execute('UNSUBSCRIBE', *patterns)

    def monitor(self):
        """Monitor to all commands in redis server"""
        pass