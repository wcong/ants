# encoding=utf8
__author__ = 'wcong'

from twisted.internet import reactor, protocol

'''
transport tools
what client should we have
co
'''


class TransportManager:
    '''
    what we do
    start a server
    start some client
    send request by client

    some times we start a tcp to a new client,
    then we what to use it,but twisted is non-block so, we do not know when the connection is available,
    but it is ok,because we could trust it until is response
    '''
    port = 8000

    def __init__(self, cluster_info):
        self.cluster_info = cluster_info
        self.client_factory = TransportClientFactory(self)
        self.server_factory = protocol.ServerFactory()
        self.server_factory.protocol = TransportServer

    def run_client(self, ip='127.0.0.1'):
        reactor.connectTCP(ip, self.port, self.client_factory)

    def send_request(self, ip, message):
        self.client_factory.client_dict[ip].send_message(message)

    def manager_data(self, data, addr):
        print 'get data from :' + addr.host + ':' + data

    def run_server(self):
        reactor.listenTCP(self.port, self.server_factory)


class TransportServer(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write('I receive you data:' + data)


class TransportClient(protocol.Protocol):
    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr

    def connectionMade(self):
        self.factory.client_dict[self.addr.host] = self

    def send_message(self, message):
        self.transport.write(message)

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        self.factory.transport_manager.manager_data(data, self.addr)

    def connectionLost(self, reason):
        del self.factory.client_dict[self.addr.host]


class TransportClientFactory(protocol.ClientFactory):
    protocol = TransportClient

    def __init__(self, transport_manager):
        self.client_dict = dict()
        self.transport_manager = transport_manager

    def buildProtocol(self, addr):
        return TransportClient(self, addr)

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()