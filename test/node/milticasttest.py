'''
test multicast
'''
__author__ = 'wcong'

import unittest
from ants.cluster import cluster
from ants.node import multicast


class MulticastTest(unittest.TestCase):
    def test(self):
        cluster = cluster.ClusterInfo(name='test_cluster')
        multicast_node = multicast.MulticastManager(cluster, self.print_result)
        multicast_node.cast()
        multicast_node.find_node()

    def print_result(self, addr):
        print 'addr:' + addr[0] + ':' + str(addr[1])


if __name__ == '__main__':
    unittest.main()