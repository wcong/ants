__author__ = 'wcong'

import unittest
import time
from scrapy.node import transport
from scrapy.cluster import cluster
from twisted.internet import reactor
import threading


class TransportTest(unittest.TestCase):
    def test(self):
        cluster = cluster.ClusterInfo(name='test_cluster')
        transport_test = transport.TransportManager(cluster)
        ip = '127.0.0.1'
        transport_test.run_server()
        transport_test.run_client(ip)
        SendRequestThread(transport_test, ip).start()
        reactor.run()


class SendRequestThread(threading.Thread):
    def __init__(self, transport_test, ip):
        super(SendRequestThread, self).__init__()
        self.transport_test = transport_test
        self.ip = ip

    def run(self):
        time.sleep(10)
        self.transport_test.send_request(self.ip, 'hello world')


if __name__ == '__main__':
    unittest.main()
