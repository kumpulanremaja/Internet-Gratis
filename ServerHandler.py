#ServerHanlder.py

import sys
import select
import socket
import random
import urlparse
import ServerInfo
import ServerConfig
import ServerSocks
import SocketServer
import BaseHTTPServer
ra = lambda text: text.decode('ascii', 'ignore')
sets = ServerConfig.Sets()
logs = False

def ServerUpdate():
    global sets
    sets = ServerConfig.Sets()


def LogWindow(flag = False):
    global logs
    logs = flag


class QueryHandler():

    def __init__(self, command = '', path = '/', headers = {}, https = False, phost = '', pport = 0):
        self.command = command
        self.path = path
        self.headers = headers
        self.https = https
        self.phost = phost
        self.pport = pport

    def get_path(self, path):
        if '/' in path:
            host, path = path.split('/', 1)
            path = '/%s' % path
        else:
            host = path
            path = '/'
        fport = False
        if self.https:
            port = 443
        else:
            port = 80
        if ':' in host:
            _host, _port = host.rsplit(':', 1)
            try:
                port = int(_port)
                host = _host
                fport = True
            except:
                pass

        return (fport,
         host,
         port,
         path)

    def get_query(self):
        if self.https:
            url = 'https://%s/' % self.path
        else:
            url = self.path
        url_scm, _, _, _, _, _ = urlparse.urlparse(url)
        if len(sets.FQUERY.split('/')) > 2:
            cgi_http = 'http/'
            if cgi_http in sets.FQUERY.lower():
                url_cgi = url.split(cgi_http)
                if len(url_cgi) > 1:
                    url = '%s://%s' % (url_scm, url_cgi.pop())
            else:
                url = url.replace(sets.FQUERY, '')
        if len(sets.MQUERY.split('/')) > 2:
            url = url.replace(sets.MQUERY, '')
        if len(sets.BQUERY.split('/')) > 2:
            url = url.replace(sets.BQUERY, '')
        url_len = len(url_scm) + 3
        url_path = url[url_len:]
        if sets.CQUERY:
            cquery_list = sets.CQUERY.split('|')
            for cquery in cquery_list:
                try:
                    old, new = cquery.split('>')
                    url_path = url_path.replace(old, new)
                except:
                    pass

        fport, host, port, path = self.get_path('%s%s' % (sets.FQUERY, url_path))
        advhost = host
        if fport and not sets.RPORT:
            path = '%s:%s%s%s%s' % (host,
             port,
             sets.MQUERY,
             path,
             sets.BQUERY)
        else:
            path = '%s%s%s%s' % (host,
             sets.MQUERY,
             path,
             sets.BQUERY)
        fport, host, port, path = self.get_path(path)
        if self.https:
            fport = True
            path = '%s:%s' % (host, port)
        elif self.phost and self.pport or sets.ADMODE:
            if sets.RQUERY:
                if sets.MQUERY.startswith('/'):
                    path = '%s%s%s' % (url[:url_len], sets.RQUERY, path)
                else:
                    path = '%s%s%s%s' % (url[:url_len],
                     sets.RQUERY,
                     sets.MQUERY,
                     path)
            elif fport and not sets.RPORT:
                path = '%s%s:%s%s' % (url[:url_len],
                 host,
                 port,
                 path)
            else:
                path = '%s%s%s' % (url[:url_len], host, path)
        else:
            _, path = path.split('/', 1)
            path = '/%s' % path
        cur_header = 'proxy-connection'
        if cur_header in self.headers and not self.phost and not self.pport:
            del self.headers[cur_header]
        cur_header = 'connection'
        if not self.https and not sets.PTYPE:
            if cur_header in self.headers:
                del self.headers[cur_header]
            self.headers[cur_header] = 'close'
        cur_header = 'host'
        if cur_header in self.headers:
            del self.headers[cur_header]
            if fport and not sets.RPORT and not self.https:
                self.headers[cur_header] = '%s:%s' % (host, port)
            else:
                self.headers[cur_header] = host
        if sets.RQUERY:
            cur_header = 'host'
            if cur_header in self.headers:
                del self.headers[cur_header]
            self.headers[cur_header] = sets.RQUERY
            cur_header = 'x-online-host'
            if cur_header in self.headers:
                del self.headers[cur_header]
            if fport and not self.https:
                self.headers[cur_header] = '%s:%s' % (host, port)
            else:
                self.headers[cur_header] = '%s' % host
        if sets.ADMODE:
            cur_header = 'host'
            if cur_header in self.headers:
                if sets.RQUERY:
                    del self.headers[cur_header]
                    self.headers[cur_header] = '%s' % sets.RQUERY
                    cur_header = 'x-online-host'
                    if cur_header in self.headers:
                        del self.headers[cur_header]
                    if fport and not self.https:
                        self.headers[cur_header] = '%s:%s' % (advhost, port)
                    else:
                        self.headers[cur_header] = '%s' % advhost
                elif self.phost and self.pport:
                    del self.headers[cur_header]
                    advhost = advhost.replace(sets.FQUERY, '').replace(sets.MQUERY, '').replace(sets.BQUERY, '')
                    if fport and not self.https:
                        self.headers[cur_header] = '%s:%s' % (advhost, port)
                    else:
                        self.headers[cur_header] = '%s' % advhost
        if sets.CUSHDR0 and not sets.VALHDR0:
            cur_header = sets.CUSHDR0.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
        if sets.CUSHDR0 and sets.VALHDR0:
            cur_header = sets.CUSHDR0.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
            self.headers[cur_header] = sets.VALHDR0
        if sets.CUSHDR1 and not sets.VALHDR1:
            cur_header = sets.CUSHDR1.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
        if sets.CUSHDR1 and sets.VALHDR1:
            cur_header = sets.CUSHDR1.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
            self.headers[cur_header] = sets.VALHDR1
        if sets.CUSHDR2 and not sets.VALHDR2:
            cur_header = sets.CUSHDR2.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
        if sets.CUSHDR2 and sets.VALHDR2:
            cur_header = sets.CUSHDR2.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
            self.headers[cur_header] = sets.VALHDR2
        if sets.CUSHDR3 and not sets.VALHDR3:
            cur_header = sets.CUSHDR3.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
        if sets.CUSHDR3 and sets.VALHDR3:
            cur_header = sets.CUSHDR3.lower()
            if cur_header in self.headers:
                del self.headers[cur_header]
            self.headers[cur_header] = sets.VALHDR3
        if sets.RPORT:
            cur_port = ':%s' % port
            path = path.replace(cur_port, '')
            cur_list = ('host', 'x-online-host')
            for cur_header in cur_list:
                if cur_header in self.headers and ':' in self.headers[cur_header]:
                    rhost, _ = self.headers[cur_header].split(':')
                    del self.headers[cur_header]
                    self.headers[cur_header] = rhost

        header = self.headers
        uahdr = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'
        cur_header = 'user-agent'
        if cur_header in self.headers:
            uahdr = self.headers[cur_header]
        self.del_garbage()
        return (path,
         header,
         uahdr,
         host,
         port,
         advhost)

    def del_garbage(self):
        del self.command
        del self.path
        del self.headers
        del self.https
        del self.phost
        del self.pport


class ProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def __getattr__(self, item):
        if item.startswith('do_'):
            return self.do_COMMAND

    def do_COMMAND(self):
        self.get_urlcheck()
        self.get_headercheck()
        self.get_recv_headers()
        self.get_proxy()
        query = QueryHandler(self.command, self.path, self.headers, self.https, self.phost, self.pport)
        self.path, self.headers, self.uahdr, self.host, self.port, self.advhost = query.get_query()
        self.get_newline()
        self.get_requestline()
        self.get_injectline()
        self.get_send_inject()
        self.get_send_headers()
        soc = self.proxy_sock()
        try:
            if self.connect_to(soc, self.host, self.port, self.advhost):
                data = ra('%s%s' % (self.get_injectline(), self.newline)).encode('hex')
                for header, value in self.headers.items():
                    data += ra('%s: %s%s' % (str(header).title(), value, self.newline)).encode('hex')

                post_header = 'content-length'
                if post_header in self.headers:
                    data += ra(self.newline).encode('hex')
                    data += self.rfile.read(int(self.headers[post_header])).encode('hex')
                    data += ra(self.newline).encode('hex')
                data += ra('%s%s' % (self.newline, self.get_send_end())).encode('hex')
                data = data.decode('hex')
                while data:
                    byte = soc.send(data)
                    data = data[byte:]

                self.get_response_data(soc)
                self.send_connection_close(soc)
                self.del_garbage()
        except socket.error as msg:
            self.send_connection_error(msg)
            self.send_connection_close(soc)
            return
        except:
            return

    def do_CONNECT(self):
        if sets.RHTTPS:
            self.get_urlcheck()
            self.get_headercheck()
            self.get_recv_headers()
            self.get_proxy()
            query = QueryHandler(self.command, self.path, self.headers, self.https, self.phost, self.pport)
            self.path, self.headers, self.uahdr, self.host, self.port, self.advhost = query.get_query()
            self.get_newline()
            self.get_requestline()
            self.get_injectline()
            self.get_send_inject()
            self.get_send_headers()
            soc = self.proxy_sock()
            try:
                if self.connect_to(soc, self.host, self.port, self.advhost):
                    data = '%s 200 Connection Established\r\nProxy-Agent: %s/%s' % (self.request_version, ServerInfo.Info('name').get_info().replace(' ', ''), ServerInfo.Info('ver').get_info()[:3])
                    self.send_response_data('%s\r\n' % data)
                    self.send_response_data('\r\n')
                    self.get_response_header(data)
                    self.get_response_data(soc)
                    self.send_connection_close(soc)
                    self.del_garbage()
            except socket.error as msg:
                self.send_connection_error(msg)
                self.send_connection_close(soc)
                return
            except:
                return

        else:
            self.send_connection_error((501, 'method not allowed'))
            self.connection.close()
            return

    def get_urlcheck(self):
        self.https = False
        if self.command == 'CONNECT':
            self.https = True

    def get_headercheck(self):
        header_check = {}
        for header, value in self.headers.items():
            if header.find('\t') == -1 and header.find('\t') == -1:
                header_check[str(header).lower()] = value

        self.headers = header_check

    def get_proxy(self):
        self.phost = ''
        self.pport = 0
        self.puser = None
        self.ppass = None
        if ':' in sets.PHOST and not sets.PPORT:
            plist = sets.PHOST.split('>')
            count = len(plist)
            while 1:
                count -= 1
                if count >= 0:
                    plist = plist[random.randint(0, len(plist) - 1)]
                    if '@' in plist and plist:
                        try:
                            self.puser, self.ppass = plist.split('@')[1].split(':')
                            plist = plist.split('@')[0]
                        except:
                            pass

                    if ':' in plist and plist:
                        try:
                            self.phost, self.pport = plist.split(':')
                            self.pport = int(self.pport)
                        except:
                            pass

                        break
                else:
                    break

        elif sets.PHOST and sets.PPORT:
            self.phost, self.pport = sets.PHOST, sets.PPORT
        return

    def proxy_sock(self):
        if sets.IQUERY and self.https or self.https:
            data = ra('%s%s' % (self.get_injectline(), self.newline))
            for header, value in self.headers.items():
                data += ra('%s: %s%s' % (str(header).title(), value, self.newline))

            soc = ServerSocks.socksocket(headers=data, newline=self.newline)
        else:
            soc = ServerSocks.socksocket(newline=self.newline)
        if self.phost and self.pport:
            soc.setproxy(sets.PTYPE, self.phost, self.pport, rdns=True, username=self.puser, password=self.puser, useragent=self.uahdr)
        return soc

    def connect_to(self, soc, host, port, advhost):
        try:
            if sets.ADMODE:
                host, port = advhost, port
            soc.setblocking(1)
            soc.connect((host, port))
            return 1
        except socket.error as msg:
            self.send_connection_error(msg)
            self.send_connection_close(soc)
            return 0
        except:
            return 0

    def get_newline(self):
        self.newline = ['\r\n', '\n'][sets.ILINE]

    def get_requestline(self):
        if sets.RHTTP == 1:
            self.request_version = 'HTTP/1.0'
        elif sets.RHTTP == 2:
            self.request_version = 'HTTP/1.1'
        self.requestline = '%s %s %s' % (self.command, self.path, self.request_version)

    def get_injectline(self):
        if sets.IQUERY:
            meth = ['HEAD',
             'GET',
             'POST',
             'DELETE',
             'CONNECT',
             'OPTIONS',
             'TRACE',
             'PUT'][sets.IMETHOD]
            if '/' in sets.IQUERY:
                host, path = sets.IQUERY.split('/', 1)
                path = '/%s' % path
            else:
                host = sets.IQUERY
                path = '/'
            if self.phost and self.pport or sets.ADMODE:
                path = 'http://%s%s' % (host, path)
            self.splitline = self.newline * 3
            if sets.ISPLIT:
                self.splitline = self.newline * sets.ISPLIT
            self.injectline = '%s %s HTTP/1.1%sHost: %s%s' % (meth,
             path,
             self.newline,
             host, self.splitline)
            return '%s%s' % (self.injectline, self.requestline)
        else:
            return self.requestline

    def get_send_end(self):
        if sets.IQUERY:
            return self.newline
        else:
            return ''

    def get_recv_headers(self):
        self.send_connection_logger('+++Receive Request+++\r\nFrom Address - %s:%s\r\n%s\r\n' % (self.client_address[0], self.client_address[1], self.requestline))
        for header, value in self.headers.items():
            self.send_connection_logger('%s: %s\r\n' % (str(header).title(), value))

        self.send_connection_logger('\r\n')

    def get_send_inject(self):
        if sets.IQUERY:
            self.send_connection_logger('+++Send Inject+++\r\n')
            if self.phost and self.pport:
                self.send_connection_logger('Using Proxy - %s:%s\r\n' % (self.phost, self.pport))
            elif sets.ADMODE:
                self.send_connection_logger('Using Host - %s:%s\r\n' % (self.advhost, self.port))
            else:
                self.send_connection_logger('Using Server - %s:%s\r\n' % (self.host, self.port))
            for inject in self.splitline[0].split(self.newline):
                self.send_connection_logger('%s' % inject)

            self.send_connection_logger('\r\n')

    def get_send_headers(self):
        self.send_connection_logger('+++Send Request+++\r\n')
        if self.phost and self.pport:
            self.send_connection_logger('Using Proxy - %s:%s\r\n' % (self.phost, self.pport))
        elif sets.ADMODE:
            self.send_connection_logger('Using Host - %s:%s\r\n' % (self.advhost, self.port))
        else:
            self.send_connection_logger('Using Server - %s:%s\r\n' % (self.host, self.port))
        self.send_connection_logger('%s\r\n' % self.requestline)
        for header, value in self.headers.items():
            self.send_connection_logger('%s: %s\r\n' % (str(header).title(), value))

        self.send_connection_logger('\r\n')

    def find_double_newline(self, data):
        pos1 = data.find('\n\r\n')
        if pos1 >= 0:
            pos1 += 3
        pos2 = data.find('\n\n')
        if pos2 >= 0:
            pos2 += 2
        if pos1 >= 0:
            if pos2 >= 0:
                return min(pos1, pos2)
            else:
                return pos1
        else:
            return pos2

    def get_data_splitter(self, data):
        if data.split('\r\n\r\n')[0].split(' ')[0] in ('HTTP/0.9', 'HTTP/1.0', 'HTTP/1.1'):
            return 1
        else:
            return 0

    def get_response_header(self, data):
        if not self.https:
            index = self.find_double_newline(data)
            if index >= 0:
                data = str(data[:index].split('\r\n\r\n')[0])
                if self.get_data_splitter(data):
                    self.send_connection_logger('+++Receive Response+++\r\n%s\r\n' % data)
                    self.send_connection_logger('\r\n')
        elif self.get_data_splitter(data):
            self.send_connection_logger('+++Receive Response+++\r\n%s\r\n' % data)
            self.send_connection_logger('\r\n')

    def get_response_data(self, soc):
        iw = [self.connection, soc]
        ow = []
        count = 0
        timeout = 0
        while 1:
            timeout += 1
            ins, _, exs = select.select(iw, ow, iw, 3)
            if exs:
                break
            if ins:
                for resp in ins:
                    try:
                        data = resp.recv(sets.SBUFF)
                        if data:
                            if resp is soc:
                                if sets.IQUERY:
                                    if self.get_data_splitter(data):
                                        count += 1
                                    if not self.https:
                                        if count % 2 == 0:
                                            count = 0
                                            self.get_response_header(data)
                                            self.send_response_data(data)
                                    else:
                                        for idata in data.split('\r\n\r\n'):
                                            if count == 1 and not idata.startswith('HTTP/'):
                                                self.send_response_data(idata)

                                else:
                                    self.get_response_header(data)
                                    self.send_response_data(data)
                            else:
                                while data:
                                    byte = soc.send(data)
                                    data = data[byte:]

                            timeout = 0
                        else:
                            break
                    except:
                        break

            if timeout == sets.TIMEOUT:
                break

    def send_response_data(self, data):
        self.wfile.write(data)

    def send_connection_close(self, soc):
        soc.close()
        self.connection.close()

    def send_connection_error(self, msg, page = True):
        try:
            code, message = msg
        except:
            self.send_connection_error((501, 'unknown error'))

        message = str(message).capitalize()
        self.send_connection_logger('+++Connection Error+++\r\n')
        self.send_connection_logger('%s: %s\r\n\r\n' % (str(code), message))
        if page:
            self.send_error(502, '%s.' % message)

    def send_connection_logger(self, data):
        if logs:
            sys.stderr.write(data)

    def del_garbage(self):
        del self.https
        del self.path
        del self.headers
        del self.uahdr
        del self.host
        del self.port
        del self.advhost
        del self.newline
        del self.requestline
        del self.injectline
        del self.phost
        del self.pport
        del self.puser
        del self.ppass


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

    def handle_error(self, request, client_address):
        pass


class HTTPProxyService():

    def __init__(self):
        self.httpd = ThreadingHTTPServer((sets.LHOST, sets.LPORT), ProxyHandler)
        self.httpd.allow_reuse_address = True

    def serve_forever(self):
        self.httpd.serve_forever()