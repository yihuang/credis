class Reader(object):
    def __init__(self, protocolError, replyError, encoding=None):
        self.protocolError = protocolError
        self.replyError = replyError
        self.encoding = encoding
        self._buffer = ''

    def gets(self):
        buf = self._buffer
        byte, response = byte_to_chr(buf[0]), buf[1:]

        if byte not in ('-', '+', ':', '$', '*'):
            return self.protocolError("Protocol Error: %s, %s" %
                                  (str(byte), str(response)))

        # server returned an error
        if byte == '-':
            response = nativestr(response)
            return self.replyError(response)
        elif byte == '+':
            pass
        elif byte == ':':
            response = long(response)
        elif byte == '$':
            length = int(response)
            if length == -1:
                return None
            response = buf.read(length)

    def feed(self, buf):
        self._buffer += buf
