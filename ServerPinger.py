import random
import urllib2
import ServerConfig

class Pinger:

    def __init__(self):
        self.sets = ServerConfig.Sets()
        self.host = []
        for server in self.sets.KEEP.split('|'):
            if server:
                self.host.append(server)

    def check(self):
        if self.host:
            try:
                request = urllib2.Request('http://%s/' % self.host[random.randint(0, len(self.host) - 1)])
                request.add_header('Accept-Encoding', 'identity, *;q=0')
                request.add_header('Connection', 'close')
                proxy_handler = urllib2.ProxyHandler({'http': '%s:%s' % ('127.0.0.1', self.sets.LPORT)})
                opener = urllib2.build_opener(proxy_handler)
                urllib2.install_opener(opener)
                urllib2.urlopen(request)
            except:
                pass