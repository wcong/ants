__author__ = 'wcong'

import unittest
import time
from ants.node import transport
from ants import settings
from ants.node import node
from twisted.internet import reactor
import threading


class TransportTest(unittest.TestCase):
    def test(self):
        setting = settings.Settings()
        cluster = node.NodeManager(setting)
        transport_test = transport.TransportManager(cluster)
        ip = '127.0.0.1'
        transport_test.run_server()
        transport_test.run_client(ip, setting.get('TRANSPORT_PORT'))
        SendRequestThread(transport_test, ip).start()
        reactor.run()


class SendRequestThread(threading.Thread):
    def __init__(self, transport_test, ip):
        super(SendRequestThread, self).__init__()
        self.transport_test = transport_test
        self.ip = ip


    def run(self):
        time.sleep(10)
        setting = settings.Settings()
        self.transport_test.send_request(self.ip, setting.get('TRANSPORT_PORT'), 'hello world')


if __name__ == '__main__':
    unittest.main()
