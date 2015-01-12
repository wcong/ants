# encoding=utf8
__author__ = 'wcong'

from twisted.internet import reactor, protocol
from ants import manager

'''
transport tools
what client should we have
co
'''


class TransportManager(manager.Manager):
    '''
    what we do
    start a server
    start some client
    send request by client

    some times we start a tcp to a new client,
    then we what to use it,but twisted is non-block so, we do not know when the connection is available,
    but it is ok,because we could trust it until is response
    '''

    def __init__(self, setting, node_manager):
        self.setting = setting
        self.port = self.setting.get('TRANSPORT_PORT')
        self.node_manager = node_manager
        self.client_factory = TransportClientFactory(self)
        self.server_factory = protocol.ServerFactory()
        self.server_factory.protocol = TransportServer

    def start(self):
        self.run_server()

    def stop(self):
        pass

    def run_client(self, ip, port):
        reactor.connectTCP(ip, port, self.client_factory)

    def send_request(self, ip, message):
        self.client_factory.client_dict[ip].send_message(message)

    def manager_data(self, data, addr):
        print 'get data from :' + addr.host + ':' + data

    def run_server(self):
        reactor.listenTCP(self.port, self.server_factory)

    def connect_made(self, ip, port):
        self.node_manager.cluster_manager.add_node()


class TransportServer(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write('I receive you data:' + data)


class TransportClient(protocol.Protocol):
    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr

    def connectionMade(self):
        self.factory.client_dict[self.addr.host] = self
        self.factory.transport_manager.connect_made(self.addr.host)

    def send_message(self, message):
        self.transport.write(message)

    def dataReceived(self, data):
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