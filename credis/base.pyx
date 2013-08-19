cdef bytes SYM_STAR = b'*'
cdef bytes SYM_DOLLAR = b'$'
cdef bytes SYM_CRLF = b'\r\n'
cdef bytes SYM_LF = b'\n'

cdef extern from "Python.h":
    object PyObject_Str(object v)

DEF CHAR_BIT = 8

cdef object int_to_decimal_string(Py_ssize_t n):
    # sizeof(long)*CHAR_BIT/3+6
    cdef char buf[32], *p, *bufend
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
    "Manages TCP communication to and from a Redis server"

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

    def __init__(self, host='localhost', port=6379, db=0, password=None,
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
        "Connects to the Redis server if not already connected"
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
        "Create a TCP/UNIX socket connection"
        if self.path is not None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.path)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
        sock.settimeout(self.socket_timeout)
        return sock

    cdef _error_message(self, exception):
        # args for socket.error can either be (errno, "message")
        # or just "message"
        address = self.path is None and '(%s:%s)'%(self.host, self.port) \
                                    or self.path
        return "Error connecting to %s. %s." % \
            (address, exception.args)

    cdef _init_connection(self):
        "Initialize the connection, authenticate and select a database"

        # if a password is specified, authenticate
        if self.password is not None:
            self.send_command(('AUTH', self.password))
            if <basestring>self.read_response() != 'OK':
                raise AuthenticationError('Invalid Password')

        # if a database is specified, switch to it
        if self.db is not None:
            self.send_command(('SELECT', self.db))
            if <basestring>self.read_response() != 'OK':
                raise ConnectionError('Invalid Database')

    cpdef disconnect(self):
        "Disconnects from the Redis server"
        self._reader = None
        if self._sock is None:
            return
        try:
            self._sock.close()
        except socket.error:
            pass
        self._sock = None

    cpdef send_packed_command(self, command):
        "Send an already packed command to the Redis server"
        if not self._sock:
            self.connect()
        try:
            self._sock.sendall(command)
        except socket.error as e:
            self.disconnect()
            raise ConnectionError("Error while writing to socket. %s." %
                                  (e.args))
        except:
            self.disconnect()
            raise

    cpdef send_command(self, tuple args):
        "Pack and send a command to the Redis server"
        self.send_packed_command(self._pack_command(args))

    cdef _read_response(self):
        response = self._reader.gets()
        while response is False:
            try:
                buffer = self._sock.recv(4096)
            except (socket.error, socket.timeout) as e:
                raise ConnectionError("Error while reading from socket: %s" %
                                      (e.args,))
            if not buffer:
                raise RedisReplyError("Socket closed on remote end")
            self._reader.feed(buffer)
            # proactively, but not conclusively, check if more data is in the
            # buffer. if the data received doesn't end with \n, there's more.
            if not buffer.endswith(SYM_LF):
                continue
            response = self._reader.gets()
        return response

    cpdef read_response(self):
        "Read the response from a previously sent command"
        try:
            return self._read_response()
        except:
            self.disconnect()
            raise

    cdef bytes _encode(self, value):
        "Return a bytestring representation of the value"
        if isinstance(value, bytes):
            return value
        if isinstance(value, int):
            return int_to_decimal_string(<int>value)
        if isinstance(value, unicode):
            if self.encoding is None and self.encoding_errors is None:
                return (<unicode>value).encode('utf-8')
            else:
                return (<unicode>value).encode(self.encoding is not None or 'utf-8',
                                               self.encoding_errors is not None or 'strict')
        if not isinstance(value, basestring):
            return PyObject_Str(value)

    cdef _pack_command_list(self, list output, tuple args):
        cdef bytes enc_value
        output.append(SYM_STAR)
        output.append(int_to_decimal_string(len(args)))
        output.append(SYM_CRLF)
        for value in args:
            enc_value = self._encode(value)
            output.append(SYM_DOLLAR)
            output.append(int_to_decimal_string(len(enc_value)))
            output.append(SYM_CRLF)
            output.append(enc_value)
            output.append(SYM_CRLF)

    cdef _pack_command(self, tuple args):
        "Pack a series of arguments into a value Redis command"
        cdef list output = []
        self._pack_command_list(output, args)
        return b''.join(output)

    cdef _pack_pipeline_command(self, stack):
        "Pack a series of arguments into a value Redis command"
        cdef list output = []
        cdef tuple args
        for args in stack:
            self._pack_command_list(output, args)
        return b''.join(output)

    def send_pipeline(self, stack):
        self.send_packed_command(self._pack_pipeline_command(stack))
