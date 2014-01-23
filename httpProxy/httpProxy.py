import BaseHTTPServer
import socket
import SocketServer
import urlparse
import datetime

import select
__version__ = '0.0.2'
wan_host = '192.168.5.1:80'
from util import get_wan_url



class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    version_string = 'lianwo breaker '+__version__
    rbufsize=0
    def _connect_to(self, netloc, soc):
       
        i = netloc.find(':')
        if i>=0:
            host_port = netloc[:i], int(netloc[i+1:])

        else:
            host_port = netloc, 80
        print '\t connecting to %s:%s' % host_port,
        try:
            soc.connect(host_port)
        except socket.error, arg:
            try:
                msg=arg[1]
            except:
                msg=arg
            print 'connection failed'
            self.send_error(404,msg)
            return 0
        print 'connected'
        return 1
    def do_CONNECTION(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._connnect_to(self.path, soc):
            self.log_request(200)

            self.wfile.write(self.protocol_version+
                             " 200 Connection established\r\\n")
            self.wfile.write("Proxy-agent: %s\r\n" % self.version_string)
            self.wfile.write("\r\n")
            self._read_write(soc)

    def do_GET(self):
        '''handle GET request'''
        (scm, netloc, path,params,query, fragment) = urlparse.urlparse(self.path, 'http')
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'the request is:',scm+netloc+path
        print 'params:', params,
        print 'query:', query
        
        if netloc == wan_host:
            pass
        else:
            print 'debug:',netloc+path
            path = get_wan_url(netloc+path)
            netloc = wan_host
        print 'final request',netloc,path
        if self._connect_to(netloc, soc):
            soc.send("%s %s %s\r\n" %
                     (self.command,
                      urlparse.urlunparse(('','',path,params,query,'')),
                      self.request_version)
                     )
            for key_val in self.headers.items():
                soc.send("%s: %s\r\n"%key_val)

            soc.send('\r\n')
            self._read_write(soc)
        soc.close()
        self.connection.close()
    do_HEAD = do_GET
    do_POST = do_GET

    def _read_write(self, soc, max_idling=20):
        iw = [self.connection, soc]
        ow = []
        count = 0
        while 1:
            count +=1
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs:break
            if ins:
                for i in ins:
                    if i is soc:
                        out = self.connection
                    else:
                        out = soc
                    data = i.recv(8192)
                    if data:
                        out.send(data)
                        count = 0
            else:
                print '.',
            if count == max_idling:break



class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer):pass

if __name__ == '__main__':
    from sys import argv
    print get_wan_url('http://www.baidu.com')

    BaseHTTPServer.test(ProxyHandler, ThreadingHTTPServer)

