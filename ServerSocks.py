#Embedded file name: ServerSocks.py

import socket
import base64
if getattr(socket, 'socket', None) is None:
    raise ImportError('socket.socket missing, proxy support unusable')
ra = lambda text: text.decode('ascii', 'ignore')
_defaultproxy = None
_orgsocket = socket.socket

class ProxyError(Exception):
    pass


class GeneralProxyError(ProxyError):
    pass


class HTTPError(ProxyError):
    pass


_generalerrors = ('success', 'invalid data', 'not connected', 'not available', 'bad proxy type', 'bad input')

def setdefaultproxy(proxytype = None, addr = None, port = None, rdns = True, username = None, password = None, useragent = None):
    global _defaultproxy
    _defaultproxy = (proxytype,
     addr,
     port,
     rdns,
     username,
     password,
     useragent)


def wrapmodule(module):
    if _defaultproxy != None:
        module.socket.socket = socksocket
    else:
        raise GeneralProxyError((4, 'no proxy specified'))
    return


class socksocket(socket.socket):

    def __init__(self, family = socket.AF_INET, tipe = socket.SOCK_STREAM, proto = 0, _sock = None, headers = None, newline = None):
        _orgsocket.__init__(self, family, tipe, proto, _sock)
        if _defaultproxy != None:
            self.__proxy = _defaultproxy
        else:
            self.__proxy = (None, None, None, None, None, None, None)
        self.__proxysockname = None
        self.__proxypeername = None
        self.__httptunnel = True
        self.__headers = headers
        self.__newline = newline
        return

    def __recvall(self, count):
        data = self.recv(count)
        while len(data) < count:
            d = self.recv(count - len(data))
            if not d:
                raise GeneralProxyError((0, 'connection closed unexpectedly'))
            data = data + d

        return data

    def sendall(self, content, *args):
        if not self.__httptunnel:
            content = self.__rewriteproxy(content)
        return super(socksocket, self).sendall(content, *args)

    def __rewriteproxy(self, header):
        host, endpt = (None, None)
        hdrs = header.split('%s' % self.__newline)
        for hdr in hdrs:
            if hdr.lower().startswith('host:'):
                host = hdr
            elif hdr.lower().startswith('get') or hdr.lower().startswith('post'):
                endpt = hdr

        if host and endpt:
            hdrs.remove(host)
            hdrs.remove(endpt)
            host = host.split(' ')[1]
            endpt = endpt.split(' ')
            if self.__proxy[4] != None and self.__proxy[5] != None:
                hdrs.insert(0, self.__getauthheader())
            hdrs.insert(0, 'Host: %s' % host)
            hdrs.insert(0, '%s http://%s%s %s' % (endpt[0],
             host,
             endpt[1],
             endpt[2]))
        return '%s' % self.__newline.join(hdrs)

    def __getauthheader(self):
        auth = self.__proxy[4] + ':' + self.__proxy[5]
        return 'Proxy-Authorization: Basic ' + base64.b64encode(auth)

    def setproxy(self, proxytype = None, addr = None, port = None, rdns = True, username = None, password = None, useragent = None):
        self.__proxy = (proxytype,
         addr,
         port,
         rdns,
         username,
         password,
         useragent)

    def getproxysockname(self):
        return self.__proxysockname

    def getproxypeername(self):
        return _orgsocket.getpeername(self)

    def getpeername(self):
        return self.__proxypeername

    def __negotiatehttp(self, destaddr, destport):
        if not self.__proxy[3]:
            addr = socket.gethostbyname(destaddr)
        else:
            addr = destaddr
        if self.__headers:
            headers = [self.__headers]
        else:
            headers = ['CONNECT ',
             addr,
             ':',
             str(destport),
             ' HTTP/1.1%s' % self.__newline]
            headers += ['Host: ', destaddr, '%s' % self.__newline]
            if self.__proxy[6] is not None:
                headers += ['User-Agent: ', unicode(self.__proxy[6]), '%s' % self.__newline]
        if self.__proxy[4] != None and self.__proxy[5] != None:
            headers += [self.__getauthheader(), '%s' % self.__newline]
        headers.append('%s' % self.__newline)
        self.sendall(ra(''.join(headers).encode()))
        resp = self.recv(1)
        while resp.find('\r\n\r\n'.encode()) == -1:
            resp = resp + self.recv(1)

        self.__proxysockname = ('0.0.0.0', 0)
        self.__proxypeername = (addr, destport)
        return

    def connect(self, destpair):
        if type(destpair) not in (list, tuple) or len(destpair) < 2 or not isinstance(destpair[0], basestring) or type(destpair[1]) != int:
            raise GeneralProxyError((5, _generalerrors[5]))
        if self.__proxy[0] == 0:
            if self.__proxy[2] != None:
                portnum = self.__proxy[2]
            else:
                portnum = 8080
            _orgsocket.connect(self, (self.__proxy[1], portnum))
            _ports = (22, 443, 465, 563, 585, 587, 636, 706, 993, 995, 2083, 2211, 2483, 2949, 4747, 6679, 6697, 8883, 19999)
            if destpair[1] in _ports:
                self.__negotiatehttp(destpair[0], destpair[1])
            else:
                self.__httptunnel = False
        elif self.__proxy[0] == 1:
            if self.__proxy[2] != None:
                portnum = self.__proxy[2]
            else:
                portnum = 8080
            _orgsocket.connect(self, (self.__proxy[1], portnum))
            self.__negotiatehttp(destpair[0], destpair[1])
        elif self.__proxy[0] == None:
            _orgsocket.connect(self, (destpair[0], destpair[1]))
        else:
            raise GeneralProxyError((4, _generalerrors[4]))
        return