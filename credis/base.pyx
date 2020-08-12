cdef bytes SYM_STAR = b'*'
cdef bytes SYM_DOLLAR = b'$'
cdef bytes SYM_CRLF = b'\r\n'
cdef bytes SYM_LF = b'\n'

from cpython.tuple cimport PyTuple_New, PyTuple_SetItem
from cpython.ref cimport Py_INCREF
from cpython.long cimport PyLong_AsLong
from cpython.exc cimport PyErr_ExceptionMatches, PyErr_Occurred, PyErr_Clear

# portable with python2.6
cdef long PyLong_AsLongAndOverflow(object o, int *overflow) except? -1:
    cdef long ret
    try:
        ret = PyLong_AsLong(o)
    except OverflowError:
        overflow[0] = 1
        return -1

    overflow[0] = 0
    return ret


DEF CHAR_BIT = 8

cdef object int_to_decimal_string(long n):
    # sizeof(long)*CHAR_BIT/3+6
    cdef char buf[32]
    cdef char *p
    cdef char *bufend
    cdef unsigned long absn
    cdef char c = '0'
    p = bufend = buf + sizeof(buf)
    if n < 0:
        absn = 0UL - n
    else:
        absn = n
    while True:
        p -= 1
        p[0] = c + (absn % 10)
        absn /= 10
        if absn == 0:
            break
    if n < 0:
        p -= 1
        p[0] = '-'
    return p[:(bufend-p)]

cdef bytes simple_bytes(s):
    if isinstance(s, unicode):
        return (<unicode>s).encode('latin-1')
    elif isinstance(s, bytes):
        return s
    else:
        s = str(s)
        if isinstance(s, unicode):
            return (<unicode>s).encode('latin-1')
        else:
            return s

import socket
import hiredis

class RedisProtocolError(Exception):
    pass

class RedisReplyError(Exception):
    pass

class ConnectionError(Exception):
    pass

class AuthenticationError(Exception):
    pass

cdef class Connection(object):
    """Manages TCP communication to and from a Redis server"""

    cdef object host
    cdef object port
    cdef object db
    cdef object password
    cdef object socket_timeout
    cdef object encoding
    cdef object encoding_errors
    cdef bint decode_responses
    cdef object path

    cdef public object _sock
    cdef public object _reader

    def __init__(self, host='localhost', port=6379, db=None, password=None,
                 socket_timeout=None, encoding='utf-8', path=None,
                 encoding_errors='strict', decode_responses=False,
                 ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.socket_timeout = socket_timeout
        if encoding != 'utf-8':
            self.encoding = encoding
        else:
            self.encoding = None # default to use utf-8 encoding
        self.path = path
        if encoding_errors != 'strict':
            self.encoding_errors = encoding_errors
        else:
            self.encoding_errors = None # default to strict
        self.decode_responses = decode_responses

        self._sock = None
        self._reader = None

    def __del__(self):
        try:
            self.disconnect()
        except:
            pass

    def connect(self):
        """Connects to the Redis server if not already connected"""
        if self._sock:
            return

        try:
            sock = self._connect()
        except socket.error as e:
            raise ConnectionError(self._error_message(e))

        self._sock = sock
        kwargs = {
            'protocolError': RedisProtocolError,
            'replyError': RedisReplyError,
        }
        if self.decode_responses:
            kwargs['encoding'] = self.encoding or 'utf-8'
        self._reader = hiredis.Reader(**kwargs)

        self._init_connection()

    cdef _connect(self):
        """Create a TCP/UNIX socket connection"""
        if self.path is not None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(self.socket_timeout)
            sock.connect(self.path)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.socket_timeout)
            sock.connect((self.host, self.port))
        return sock

    cdef _error_message(self, exception):
        # args for socket.error can either be (errno, "message")
        # or just "message"
        address = self.path is None and '(%s:%s)'%(self.host, self.port) \
                                    or self.path
        return "Error connecting to %s. %s." % \
            (address, exception.args)

    cdef _init_connection(self):
        """Initialize the connection, authenticate and select a database"""

        # if a password is specified, authenticate
        if self.password is not None:
            self.send_command(('AUTH', self.password))
            reply = self.read_response()
            if isinstance(reply, Exception):
                self.disconnect()
                raise reply
            if reply.decode() != 'OK':
                self.disconnect()
                raise AuthenticationError('Invalid Password')

        # if a database is specified, switch to it
        if self.db is not None:
            self.send_command(('SELECT', self.db))
            reply = self.read_response()
            if isinstance(reply, Exception):
                self.disconnect()
                raise reply
            if reply.decode() != 'OK':
                self.disconnect()
                raise ConnectionError('Invalid Database')

    cpdef disconnect(self):
        """Disconnects from the Redis server"""
        self._reader = None
        if self._sock is None:
            return
        try:
            self._sock.close()
        except socket.error:
            pass
        self._sock = None

    cpdef send_packed_command(self, commands):
        """Send an already packed command to the Redis server"""
        if not self._sock:
            self.connect()
        cdef object sendall = self._sock.sendall
        try:
            for command in commands:
                sendall(command)
        except socket.error as e:
            self.disconnect()
            raise ConnectionError("Error while writing to socket. %s." %
                                  (e.args,))
        except:
            self.disconnect()
            raise

    cpdef send_command(self, args):
        """Pack and send a command to the Redis server"""
        self.send_packed_command(self._pack_command(args))

    cdef _read_response(self):
        response = self._reader.gets()

        cdef object recv = self._sock.recv
        while response is False:
            try:
                buffer = recv(4096)
            except (socket.error, socket.timeout) as e:
                raise ConnectionError("Error while reading from socket: %s" %
                                      (e.args,))
            if not buffer:
                raise ConnectionError("Socket closed on remote end")
            self._reader.feed(buffer)
            # proactively, but not conclusively, check if more data is in the
            # buffer. if the data received doesn't end with \n, there's more.
            if not buffer.endswith(SYM_LF):
                continue
            response = self._reader.gets()
        return response

    cpdef read_response(self):
        """Read the response from a previously sent command"""
        try:
            return self._read_response()
        except:
            self.disconnect()
            raise

    cpdef read_n_response(self, int n):
        cdef result = PyTuple_New(n)
        cdef int i
        cdef object o
        for i in range(n):
            o = self.read_response()
            Py_INCREF(o)
            PyTuple_SetItem(result, i, o)
        return result

    cpdef bytes _encode(self, value):
        """Return a bytestring representation of the value"""
        cdef int overflow = 0
        cdef long n = 0

        if isinstance(value, bytes):
            return value

        if isinstance(value, int):
            n = PyLong_AsLongAndOverflow(value, &overflow)
            if overflow == 0:
                return int_to_decimal_string(n)

        if isinstance(value, float):
            return simple_bytes(repr(value))

        if not isinstance(value, unicode):
            value = str(value)

        if isinstance(value, unicode):
            if self.encoding is None and self.encoding_errors is None:
                return (<unicode>value).encode('utf-8')
            else:
                return (<unicode>value).encode(self.encoding is not None or 'utf-8',
                                               self.encoding_errors is not None or 'strict')
        return value

    cdef _pack_command_list(self, args):
        cdef bytes enc_value
        cdef list chunks = []
        cdef list chunk = [SYM_STAR, int_to_decimal_string(len(args)), SYM_CRLF]
        cdef int chunk_size = 0
        for s in chunk:
            chunk_size += len(s)

        for value in args:
            enc_value = self._encode(value)

            if chunk_size > 6000 or len(enc_value) > 6000:
                chunks.append(b''.join(chunk))
                chunk = []
                chunk_size = 0

            chunk.append(SYM_DOLLAR)
            chunk_size += len(SYM_DOLLAR)

            s = int_to_decimal_string(len(enc_value))
            chunk.append(s)
            chunk_size += len(s)

            chunk.append(SYM_CRLF)
            chunk_size += len(SYM_CRLF)

            chunk.append(enc_value)
            chunk_size += len(enc_value)

            chunk.append(SYM_CRLF)
            chunk_size += len(SYM_CRLF)

        if chunk:
            chunks.append(b''.join(chunk))

        return chunks

    cdef _pack_command(self, args):
        """Pack a series of arguments into a value Redis command"""
        return self._pack_command_list(args)

    cdef _pack_pipeline_command(self, cmds):
        """Pack a series of arguments into a value Redis command"""
        cdef list chunks = []
        cdef list chunk = []
        cdef int chunk_size = 0
        cdef object args

        for args in cmds:
            for item in self._pack_command_list(args):
                chunk.append(item)
                chunk_size += len(item)

            if chunk_size > 6000:
                chunks.append(b''.join(chunk))
                chunk = []
                chunk_size = 0

        if chunk_size > 0:
            chunks.append(b''.join(chunk))

        return chunks

    cpdef send_pipeline(self, cmds):
        self.send_packed_command(self._pack_pipeline_command(cmds))

    def execute(self, *args):
        self.send_command(args)
        reply = self.read_response()
        if isinstance(reply, Exception):
            raise reply
        return reply

    def execute_pipeline(self, *cmds):
        self.send_pipeline(cmds)
        return self.read_n_response(len(cmds))
