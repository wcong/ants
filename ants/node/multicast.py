# encodung=utf8
__author__ = 'wcong'
import socket
import threading
import time
from ants import manager

'''
this multicast file where all multicast tools

'''


def get_host_name():
    return socket.gethostbyname(socket.gethostname())


def make_receive_socket(ip, port):
    receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    receive_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receive_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    receive_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
    receive_sock.bind((ip, port))
    host = get_host_name()
    receive_sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
    receive_sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton(ip) + socket.inet_aton(host))
    return receive_sock


def make_cast_socket(ip, post):
    cast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    cast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    return cast_sock


class MulticastManager(manager.Manager):
    '''
    what we do
    start a cast
    accept a cast
    send message
    '''
    ip = '224.1.1.1'
    port = 8900
    receive_length = 22

    def __init__(self, node_manager, receive_callback=None):
        self.settings = node_manager.settings
        self.node_manager = node_manager
        self.message = self.settings.get('CLUSTER_NAME') + ':' + str(self.settings.get('TRANSPORT_PORT'))
        self.cast_sock = make_cast_socket(self.ip, self.port)
        self.receive_sock = make_receive_socket(self.ip, self.port)
        self.start_time = time.time()
        self.multicast_status = MulticastStatus()
        self.receive_callback = receive_callback


    def stop(self):
        self.stop_cast()

    def start(self):
        self.cast()

    def cast(self):
        multicast_thread = MulticastThread(self)
        multicast_thread.start()

    def stop_cast(self):
        self.multicast_status.stop()
        # let it exit by self
        time.sleep(MulticastThread.sleep_time)

    def send_message(self):
        self.cast_sock.sendto(self.message, (self.ip, self.port))

    def find_node(self):
        receive_thread = ReceiveThread(self)
        receive_thread.start()

    def get_message(self):
        data, addr = self.receive_sock.recvfrom(self.receive_length)
        return data, addr


class MulticastStatus:
    status_start = 'start'
    status_run = 'run'
    status_stop = 'stop'

    def __init__(self):
        self.status = self.status_start

    def run(self):
        self.status = self.status_run

    def stop(self):
        self.status = self.status_stop

    def is_run(self):
        return self.status == self.status_run


class ReceiveThread(threading.Thread):
    def __init__(self, multicast):
        super(ReceiveThread, self).__init__()
        self.multicast = multicast

    def run(self):
        self.multicast.multicast_status.run()
        while self.multicast.multicast_status.is_run():
            data, addr = self.multicast.get_message()
            if data == self.multicast.message:
                if self.multicast.receive_callback:
                    self.multicast.receive_callback(data, addr)


class MulticastThread(threading.Thread):
    sleep_time = 1

    def __init__(self, multicast):
        super(MulticastThread, self).__init__()
        self.multicast = multicast

    def run(self):
        self.multicast.multicast_status.run()
        while self.multicast.multicast_status.is_run():
            time.sleep(MulticastThread.sleep_time)
            self.multicast.send_message()