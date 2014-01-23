import BaseHTTPServer
import socket
import SocketServer
import urlparse
import datetime

import select
__version__ = '0.0.2'
wan_host = '192.168.5.1:80'
from util import get_wan_url, is_pic


from cStringIO import StringIO

class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    version_str = 'lianwo breaker '+__version__
    rbufsize=0
    log = StringIO()
    def _connect_to(self, netloc, soc):
       
        i = netloc.find(':')
        if i>=0:
            host_port = netloc[:i], int(netloc[i+1:])

        else:
            host_port = netloc, 80
        print 'connecting to %s:%s' % host_port,
        
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
        self.log.write('in do_CONNECTION')
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._connnect_to(self.path, soc):
            self.log_request(200)

#rfile 
#Contains an input stream, positioned at the start of the optional input data.
#wfile 
#Contains the output stream for writing a response back to the client.
#Proper adherence to the HTTP protocol must be used when writing to this stream.
            self.wfile.write(self.protocol_version+
                             " 200 Connection established\r\\n")
            self.wfile.write("Proxy-agent: %s\r\n" % self.version_str)
            self.wfile.write("\r\n")
            self._read_write(soc)

    def do_GET(self):
        '''handle GET request'''
        self.log.write('in do_GET')
        (scm, netloc, path,params,query, fragment) = urlparse.urlparse(self.path, 'http')
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log.write('the request is:'+scm+'://'+netloc+path+params+query)
        #print 'params:', params,'query:', query
        
        if netloc == wan_host:
            #request to lan server
            pass
        elif not is_pic(path):
            #html or js content
            path = get_wan_url(self.path)
            netloc = wan_host
        else:
            #pic resources
            path = get_wan_url(self.path)
            netloc = wan_host
        #print 'final request',scm+'://'+netloc+path
        if self._connect_to(netloc, soc):
            soc.send("%s %s %s\r\n" %
                     (self.command,
                      urlparse.urlunparse(('','',path,params,query,'')),
                      self.request_version)
                     )
            for key_val in self.headers.items():
                soc.send("%s: %s\r\n" % key_val)

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
                    try:
                        data = i.recv(8192)
                    except socket.error, err:
                        code = err[0]
                        print 'socket err',code,socket.errno.errorcode[code],'path',self.path

                        continue
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

    BaseHTTPServer.test(ProxyHandler, ThreadingHTTPServer)

