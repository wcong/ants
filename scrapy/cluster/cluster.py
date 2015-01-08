'''
what a cluster should have
'''
__author__ = 'wcong'
from scrapy.node import node
import discover
from scrapy import manager


class ClusterManager(manager.Manager):
    def __init__(self, cluster_info):
        self.cluster_info = cluster_info

    def start(self):
        pass

    def stop(self):
        pass


class ClusterInfo():
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.node_list = list()
        self.master_node = node.NodeInfo

    def append_node(self, node):
        self.node_list.append(node)





