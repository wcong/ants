__author__ = 'wcong'
import json
from ants import manager
import multicast
import transport
from ants.webservice import webservice
from ants.cluster import cluster
from ants.crawl import crawl
from ants.crawl import scheduler
import nodeinfo
import rpc


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
        self.node_info = nodeinfo.NodeInfo(multicast.get_host_name(), self.setting.get('TRANSPORT_PORT'))
        self.cluster_manager = cluster.ClusterManager(self)
        self.transport_manager = transport.TransportManager(self)
        self.multicast_manager = multicast.MulticastManager(self, self.cluster_manager.find_node)
        self.webservice_manager = webservice.WebServiceManager(self)

        self.manager_list = [self.cluster_manager, self.transport_manager, self.multicast_manager,
                             self.webservice_manager]

        self.crawl_client = crawl.CrawlClient(self)


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


    def is_idle(self, spider_name, node=None):
        if not node or node == self.node_info:
            if self.crawl_client.is_idle(spider_name):
                self.idle_engine_manager(spider_name, self.node_info.ip, self.node_info.port)
        else:
            self.transport_manager.send_request(node.ip, node.port, rpc.REQUEST_INIT_ENGINE + spider_name)

    def idle_engine_manager(self, spider_name, ip, port):
        self.cluster_manager.idle_engine_manager(spider_name, nodeinfo.NodeInfo(ip, port))

    def init_engine(self, spider_name, node=None):
        if not node or node == self.node_info:
            self.crawl_client.init_engine(spider_name)
            self.init_engine_manager(spider_name, self.node_info.ip, self.node_info.port)
        else:
            self.transport_manager.send_request(node.ip, node.port, rpc.REQUEST_INIT_ENGINE + spider_name)

    def init_engine_manager(self, spider_name, ip, port):
        self.cluster_manager.init_engine_manager(spider_name, nodeinfo.NodeInfo(ip, port))

    def send_request(self, request, node=None):
        if not node or node == self.node_info:
            self.crawl_client.accept_request(request.spider_name, request)
        else:
            self.transport_manager.send_request(node.ip, node.port,)



