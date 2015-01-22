# encoding=utf8
__author__ = 'wcong'

from twisted.internet import reactor, protocol
from ants import manager
import logging
import pickle
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
        self.settings = node_manager.settings
        self.port = self.settings.get('TRANSPORT_PORT')
        self.node_manager = node_manager
        self.client_factory = TransportClientFactory(self)
        self.server_factory = TransportServerFactory(self)
        self.client_dict = dict()

    def start(self):
        self.run_server()

    def stop(self):
        pass

    def run_client(self, ip, port):
        client_key = make_client_key(ip, port)
        if client_key in self.client_dict:
            return
        reactor.connectTCP(ip, port, self.client_factory)

    def send_request(self, ip, port, message):
        client_key = make_client_key(ip, port)
        self.client_dict[client_key].send_message(message)

    def manager_data(self, data, addr):
        print 'get data from :' + addr.host + ':' + data

    def run_server(self):
        logging.info('start tcp server:' + str(self.port))
        reactor.listenTCP(self.port, self.server_factory)

    def connect_made(self, ip, port):
        self.node_manager.add_node_to_cluster(ip, port)

    def add_client_dict(self, ip, port, client):
        self.client_dict[make_client_key(ip, port)] = client


def make_client_key(ip, port):
    return ip + ':' + str(port)


def request_add_me(tcp, msg):
    ip = tcp.transport.getPeer().host
    port = int(msg)
    tcp.transport_manager.run_client(ip, port)


def request_init_engine(tcp, msg):
    tcp.transport_manager.node_manager.init_engine(msg)
    return_msg = rpc.RESPONSE_INIT_REQUEST + str(tcp.transport_manager.port) + ':' + msg + ':' + 'ok'
    tcp.transport.write(return_msg)


def response_init_engine(tcp, msg):
    data = msg.split(':')
    if data[2] == 'ok':
        ip = tcp.transport.getPeer().host
        tcp.transport_manager.node_manager.init_engine_manager(data[1], ip, int(data[0]))


def request_is_spider_idle(tcp, msg):
    result = tcp.transport_manager.node_manager.is_idle(msg)
    tcp.transport.write(
        rpc.RESPONSE_SPIDER_IDLE_STATUS + str(tcp.transport_manager.port) + ':' + msg + ':' + result)


def response_spider_idle_status(tcp, msg):
    msg = msg.split(':')
    port = int(msg[0])
    spider_name = msg[1]
    is_idle = True if msg[2] == 'true' else False
    if is_idle:
        ip = tcp.transport.getPeer().host
        tcp.transport_manager.node_manager.idle_engine_manager(spider_name, ip, port)


def request_start_a_engine(tcp, msg):
    tcp.transport_manager.node_manager.start_a_engine(msg)


def request_send_request(tcp, msg):
    tcp.transport_manager.node_manager.send_request_to_client(pickle.loads(msg))


def response_send_request(tcp, msg):
    tcp.transport_manager.node_manager.send_request_to_master(pickle.loads(msg))


def request_result_of_request(tcp, msg):
    data = msg.split(':')
    tcp.transport_manager.node_manager.send_result_to_master(data[0], int(data[1]), int(data[2]), data[3])


def request_stop_engine(tcp, msg):
    tcp.transport_manager.node_manager.stop_engine(msg)
    return_msg = rpc.RESPONSE_STOP_ENGINE + str(tcp.transport_manager.port) + ':' + msg + ':' + 'ok'
    tcp.transport.write(return_msg)


def response_stop_engine(tcp, msg):
    data = msg.split(':')
    if data[2] == 'ok':
        ip = tcp.transport.getPeer().host
        tcp.transport_manager.node_manager.stop_engine_manager(data[1], ip, int(data[0]))


response_dict = dict()
response_dict[rpc.REQUEST_INIT_ENGINE] = request_init_engine
response_dict[rpc.RESPONSE_INIT_REQUEST] = response_init_engine
response_dict[rpc.REQUEST_IS_SPIDER_IDLE] = request_is_spider_idle
response_dict[rpc.RESPONSE_SPIDER_IDLE_STATUS] = response_spider_idle_status
response_dict[rpc.REQUEST_START_A_ENGINE] = request_start_a_engine
response_dict[rpc.REQUEST_ADD_ME] = request_add_me
response_dict[rpc.REQUEST_SEND_REQUEST] = request_send_request
response_dict[rpc.RESPONSE_SEND_REQUEST] = response_send_request
response_dict[rpc.RESPONSE_RESULT_OF_REQUEST] = request_result_of_request
response_dict[rpc.REQUEST_STOP_ENGINE] = request_stop_engine
response_dict[rpc.RESPONSE_STOP_ENGINE] = response_stop_engine


class TransportServerFactory(protocol.Factory):
    def __init__(self, transport_manager):
        self.transport_manager = transport_manager

    def buildProtocol(self, addr):
        return TransportServer(self.transport_manager)


class TransportServer(protocol.Protocol):
    def __init__(self, transport_manager):
        self.transport_manager = transport_manager

    def dataReceived(self, data):
        msg_list = data.split(rpc.END_SIGN)
        for msg in msg_list:
            if msg:
                type = msg[0:rpc.LENGTH]
                logging.info('get msg:' + type)
                data = msg[rpc.LENGTH:]
                response_dict[type](self, data)


class TransportClient(protocol.Protocol):
    def __init__(self, transport_manager, addr):
        self.transport_manager = transport_manager
        self.addr = addr

    def connectionMade(self):
        self.transport_manager.add_client_dict(self.addr.host, self.addr.port, self)
        self.transport_manager.connect_made(self.addr.host, self.addr.port)
        self.transport.write(rpc.REQUEST_ADD_ME + str(self.transport_manager.port))

    def send_message(self, message):
        self.transport.write(message + rpc.END_SIGN)

    def dataReceived(self, data):
        msg_list = data.split(rpc.END_SIGN)
        for msg in msg_list:
            if msg:
                type = msg[0:rpc.LENGTH]
                logging.info('get msg:' + type)
                data = msg[rpc.LENGTH:]
                response_dict[type](self, data)

    def connectionLost(self, reason):
        del self.transport_manager.client_dict[make_client_key(self.addr.host, self.addr.port)]


class TransportClientFactory(protocol.ClientFactory):
    protocol = TransportClient

    def __init__(self, transport_manager):
        self.transport_manager = transport_manager

    def buildProtocol(self, addr):
        return TransportClient(self.transport_manager, addr)

    def clientConnectionFailed(self, connector, reason):
        logging.info("Connection failed - to -" + connector.host + ':' + str(connector.port))

    def clientConnectionLost(self, connector, reason):
        logging.info("Connection lost - to -" + connector.host + ':' + str(connector.port))