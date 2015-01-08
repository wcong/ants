__author__ = 'wcong'
import json
from scrapy import manager


'''
what a node would do
init multicast
init transport
open spider
accept request and deal with it
'''


class NodeManager(manager.Manager):
    def __init__(self, cluster_manager, crawl_manager):
        self.cluster_manager = cluster_manager
        self.crawl_manager = crawl_manager


    def stop(self):
        pass

    def start(self):
        pass


class Node():
    ip = '127.0.0.1'
    port = '8200'

    def __init__(self):
        self.node_info = NodeInfo(self.ip, self.port)


class NodeInfo:
    def __init__(self, ip, port):
        self.name = hash(ip + str(port))
        self.ip = ip
        self.port = port


def make_node_info_from_transport(data):
    msg = json.loads(data)
    return NodeInfo(msg['ip'], msg['port'])