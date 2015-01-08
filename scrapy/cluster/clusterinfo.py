'''
what a cluster should have
'''
__author__ = 'wcong'
from scrapy.node import node
import discover


class ClusterInfo():
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.node_list = list()
        self.master_node = node.NodeInfo

    def append_node(self, node):
        self.node_list.append(node)





