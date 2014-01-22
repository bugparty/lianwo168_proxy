import BaseHTTPServer
import socket
import SocketServer

class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i>=0:
            host_port = netloc[:i], int(netloc[i:])

        else:
            host_port = netloc, 80
        print '\t connecting to %s:%s' % host_port
        soc.connect(host_port)
        return 1

class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
                          BaseHTTPServer.HTTPServer):pass

if __name__ == '__main__':
    from sys import argv
    
    BaseHTTPServer.test(ProxyHandler, ThreadingHTTPServer)

