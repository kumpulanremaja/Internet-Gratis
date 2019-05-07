#qpy:console
import sys
import time
import random
import threading
import ServerInfo
import ServerConfig
import ServerPinger
import ServerHandler
ru = lambda text: text.decode('utf-8', 'ignore')

class Server:

    def __init__(self):
        self.long = 8
        self.sets = ServerConfig.Sets()
        self.name = ServerInfo.Info('name').get_info()
        self.ver = ServerInfo.Info('ver').get_info()
        self.form = ServerInfo.Info('about').get_info()
        self.auth = ServerInfo.Info('by').get_info()
        self.mail = ServerInfo.Info('mail').get_info()
        self.remode = ServerInfo.Info('remode').get_info()
        self.conf = ServerConfig.conf
        self.noyes = [ru('No'), ru('Yes')]
        self.version = [ru('Default'), ru('HTTP/1.0'), ru('HTTP/1.1')]
        self.method = [ru('HEAD'),
         ru('GET'),
         ru('POST'),
         ru('DELETE'),
         ru('CONNECT'),
         ru('OPTIONS'),
         ru('TRACE'),
         ru('PUT')]
        self.line = [ru('\\r\\n'), ru('\\n')]
        self.split = [ru('Default'),
         ru('%s' % (self.line[self.sets.ILINE] * self.sets.ILINE)),
         ru('%s' % (self.line[self.sets.ILINE] * self.sets.ILINE)),
         ru('%s' % (self.line[self.sets.ILINE] * self.sets.ILINE)),
         ru('%s' % (self.line[self.sets.ILINE] * self.sets.ILINE)),
         ru('%s' % (self.line[self.sets.ILINE] * self.sets.ILINE))]

    def subs(self, data = '', cut = False):
        if data:
            data = data
        else:
            data = 'None'
        if cut:
            if len(data) > 5:
                data = '%s...' % data[:5]
        return data

    def about(self, title = ''):
        self.info = []
        self.info.append('[ %s ]%s\n' % (title, '=' * (self.long - len(title) - 5)))
        self.info.append('Name : %s\n' % self.name)
        self.info.append('Version : %s\n' % self.ver)
        self.info.append('Dev : %s\n' % self.auth)
        self.info.append('Email : %s\n' % self.mail)
        self.info.append('Remode : %s\n' % self.remode)
        self.info.append('\n\n')
        return ru(''.join(self.info))

    def config(self, title = ''):
        self.info = []
        self.info.append('[ %s ]%s\n' % (title, '=' * (self.long - len(title) - 5)))
        self.info.append('Config File :\n')
        self.info.append('- %s\n' % self.conf)
        self.info.append('Local Host :\n')
        self.info.append('- %s\n' % self.sets.LHOST)
        self.info.append('Local Port :\n')
        self.info.append('- %s\n' % str(self.sets.LPORT))
        self.info.append('HTTP Query :\n')
        self.info.append('- Front Query : %s\n' % self.subs(self.sets.FQUERY))
        self.info.append('- Middle Query : %s\n' % self.subs(self.sets.MQUERY))
        self.info.append('- Back Query : %s\n' % self.subs(self.sets.BQUERY))
        self.info.append('- Reverse Query : %s\n' % self.subs(self.sets.RQUERY))
        self.info.append('- Inject Query : %s\n' % self.subs(self.sets.IQUERY))
        self.info.append('- Inject Method : %s\n' % self.method[self.sets.IMETHOD])
        self.info.append('- Inject Newline : %s\n' % self.line[self.sets.ILINE])
        self.info.append('- Inject Splitline : %s\n' % self.split[self.sets.ISPLIT])
        self.info.append('- Remove Port : %s\n' % self.noyes[self.sets.RPORT])
        self.info.append('- Remove Path : %s\n' % self.noyes[self.sets.RPATH])
        self.info.append('- Url Replacer : %s\n' % self.subs(self.sets.CQUERY))
        self.info.append('- Request Version : %s\n' % self.version[self.sets.RHTTP])
        self.info.append('- Advanced Mode : %s\n' % self.noyes[self.sets.ADMODE])
        self.info.append('HTTP Header :\n')
        self.info.append('- Custom Header 1 : %s\n' % self.subs(self.sets.CUSHDR0))
        self.info.append('- Header Value 1 : %s\n' % self.subs(self.sets.VALHDR0))
        self.info.append('- Custom Header 2 : %s\n' % self.subs(self.sets.CUSHDR1))
        self.info.append('- Header Value 2 : %s\n' % self.subs(self.sets.VALHDR1))
        self.info.append('- Custom Header 3 : %s\n' % self.subs(self.sets.CUSHDR2))
        self.info.append('- Header Value 3 : %s\n' % self.subs(self.sets.VALHDR2))
        self.info.append('- Custom Header 4 : %s\n' % self.subs(self.sets.CUSHDR3))
        self.info.append('- Header Value 4 : %s\n' % self.subs(self.sets.VALHDR3))
        self.info.append('Server Config :\n')
        self.info.append('- Keep Server : %s\n' % self.subs(self.sets.KEEP))
        self.info.append('- HTTPS Connection : %s\n' % self.noyes[self.sets.RHTTPS])
        self.info.append('- Tunnel Proxy : %s\n' % self.noyes[self.sets.PTYPE])
        self.info.append('- Server Buffer : %s\n' % str(self.sets.SBUFF))
        self.info.append('- Connection Timeout : %s\n' % str(self.sets.TIMEOUT))
        self.info.append('Proxy Host :\n')
        self.info.append('- %s\n' % self.subs(self.sets.PHOST))
        self.info.append('Proxy Port :\n')
        self.info.append('- %s\n' % str(self.sets.PPORT))
        self.info.append('\n\n')
        return ru(''.join(self.info))

    def log(self, title = ''):
        self.info = []
        self.info.append('      %s %s\n' % (title, '' * (self.long - len(title) - 5)))
        self.info.append('\n\n')
        return ru(''.join(self.info))

    def show(self):
        sys.stderr.write(self.about('About'))
        time.sleep(1)
        sys.stderr.write(self.config('Configuration'))
        time.sleep(2)
        sys.stderr.write(self.log('========Inject Sukses======== \nReading Server:'))

    def run(self):
        ServerHandler.LogWindow(True)
        ServerHandler.HTTPProxyService().serve_forever()

    def pinger(self):
        while 1:
            time.sleep(random.randint(30, 300))
            ServerPinger.Pinger().check()


if __name__ == '__main__':
    Server().show()
    services = [threading.Thread(target=Server().run, args=()), threading.Thread(target=Server().pinger, args=())]
    for serving in services:
        serving.start()