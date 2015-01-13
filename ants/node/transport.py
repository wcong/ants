# encoding=utf8
__author__ = 'wcong'

from twisted.internet import reactor, protocol
from ants import manager
import rpc

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

    def __init__(self, node_manager):
        self.setting = node_manager.setting
        self.port = self.setting.get('TRANSPORT_PORT')
        self.node_manager = node_manager
        self.client_factory = TransportClientFactory(self)
        self.server_factory = protocol.ServerFactory()
        self.server_factory.protocol = TransportServer(self)

    def start(self):
        self.run_server()

    def stop(self):
        pass

    def run_client(self, ip, port):
        reactor.connectTCP(ip, port, self.client_factory)

    def send_request(self, ip, port, message):
        self.client_factory.client_dict[ip + ':' + port].send_message(message)

    def manager_data(self, data, addr):
        print 'get data from :' + addr.host + ':' + data

    def run_server(self):
        reactor.listenTCP(self.port, self.server_factory)

    def connect_made(self, ip, port):
        self.node_manager.cluster_manager.add_node(ip, port)


class TransportServer(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.response_dict = dict()
        self.response_dict[rpc.REQUEST_INIT_ENGINE] = self.request_init_engine
        self.response_dict[rpc.RESPONSE_INIT_REQUEST] = self.response_init_engine
        self.response_dict[rpc.REQUEST_IS_SPIDER_IDLE] = self.request_is_spider_idle
        self.response_dict[rpc.RESPONSE_SPIDER_IDLE_STATUS] = self.response_spider_idle_status


    def request_init_engine(self, msg):
        self.factory.node_manager.init_engine(msg)
        self.transport.write(rpc.RESPONSE_INIT_REQUEST + msg)

    def response_init_engine(self, msg):
        if msg == 'ok':
            self.factory.node_manager.init_engine_manager(msg, self.addr.host, self.addr.port)

    def request_is_spider_idle(self, msg):
        result = self.factory.node_manager.is_idle(msg)
        self.transport.write(rpc.RESPONSE_SPIDER_IDLE_STATUS + msg + ':' + result)

    def response_spider_idle_status(self, msg):
        msg = msg.split(':')
        spider_name = msg[0]
        is_idle = True if msg[1] == 'true' else False
        if is_idle:
            self.factory.node_manager.idle_engine_manager(spider_name, self.addr.host, self.addr.port)

    def dataReceived(self, data):
        type = data[0:rpc.LENGTH]
        msg = data[rpc.LENGTH:]
        self.response_dict[type](msg)


class TransportClient(protocol.Protocol):
    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr

    def connectionMade(self):
        self.factory.client_dict[self.addr.host] = self
        self.factory.transport_manager.connect_made(self.addr.host, self.addr.port)

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