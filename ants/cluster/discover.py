'''
found other node
'''
from ants import log
from ants.node import multicast

__author__ = 'wcong'


class Discover:
    def __init__(self, cluster_info):
        self.cluster_info = cluster_info
        self.local_host = multicast.get_host_name()

    def discover(self):
        multicast_node = multicast.Multicast(self.cluster_info, self.find_node_callback)
        multicast_node.cast()
        multicast_node.find_node()

    def find_node_callback(self):
        log.msg("nothing?")










