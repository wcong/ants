__author__ = 'wcong'
import json
from ants import manager
import multicast
import transport
from ants.webservice import webservice
from ants.cluster import cluster
from ants.crawl import crawl
from twisted.internet import defer


'''
what a node would do
init multicast
init transport
init web service
open spider

accept request and deal with it
'''


class NodeManager(manager.Manager):
    def __init__(self, setting):
        self.setting = setting
        self.node_info = NodeInfo(multicast.get_host_name(), self.setting.get('TRANSPORT_PORT'))
        self.cluster_manager = cluster.ClusterManager(setting, self.node_info)
        self.crawl_manager = crawl.CrawlManager(self.setting, self)
        self.transport_manager = transport.TransportManager(setting, self)
        self.multicast_manager = multicast.MulticastManager(self.setting, self, self.cluster_manager.find_node())
        self.webservice_manager = webservice.WebServiceManager(self.setting, self, self.crawl_manager)

        self.manager_list = [self.cluster_manager, self.crawl_manager, self.transport_manager, self.multicast_manager,
                             self.webservice_manager]


    def stop(self):
        for inner_manager in self.manager_list:
            inner_manager.stop()


    def start(self):
        '''
        we start all the manager
        find node
        and ready to start
        :return:
        '''
        for inner_manager in self.manager_list:
            inner_manager.start()
        self.multicast_manager.find_node()


    def start_a_crawl(self, spider_name):
        self.cluster_manager.start_a_crawl(spider_name)


class NodeInfo:
    def __init__(self, ip, port):
        self.name = hash(ip + str(port))
        self.ip = ip
        self.port = port

    def __eq__(self, other):
        return self.name == other.name


def make_node_info_from_transport(data):
    msg = json.loads(data)
    return NodeInfo(msg['ip'], msg['port'])