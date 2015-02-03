__author__ = 'wcong'
import pickle
import logging

import multicast
import transport
from ants.webservice import webservice
from ants.cluster import cluster
from ants.crawl import crawl, spidermanager
import nodeinfo
import rpc
from ants.utils import manager


'''
what a node would do
init multicast
init transport
init web service
open spider

accept request and deal with it
'''


class NodeManager(manager.Manager):
    def __init__(self, settings):
        self.settings = settings
        self.spider_manager = spidermanager.SpiderManager(self.settings.get('SPIDER_MODULES'))
        self.node_info = nodeinfo.NodeInfo(multicast.get_host_name(), self.settings.get('TRANSPORT_PORT'))
        self.cluster_manager = cluster.ClusterManager(self)
        self.transport_manager = transport.TransportManager(self)
        self.multicast_manager = multicast.MulticastManager(self, self.cluster_manager.find_node)
        self.webservice_manager = webservice.WebServiceManager(self)

        # net work manager should start first
        self.manager_list = [
            self.transport_manager,
            self.multicast_manager,
            self.cluster_manager,
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
        logging.info('start to init manager')
        for inner_manager in self.manager_list:
            inner_manager.start()

    def connect_to_node(self, ip, port):
        if ip == self.node_info.ip and port == self.node_info.port:
            return
        self.transport_manager.run_client(ip, port)

    def add_node_to_cluster(self, ip, port):
        self.cluster_manager.add_node(ip, port)

    def init_engine(self, spider_name, node=None):
        if not node or node == self.node_info:
            self.crawl_client.init_engine(spider_name)
            if self.node_info == self.cluster_manager.cluster_info.master_node:
                self.init_engine_manager(spider_name, self.node_info.ip, self.node_info.port)
        else:
            self.transport_manager.send_request(node.ip, node.port, rpc.REQUEST_INIT_ENGINE + spider_name)

    def stop_engine(self, spider_name, node=None):
        if not node or node == self.node_info:
            self.crawl_client.stop_engine(spider_name)
            if self.node_info == self.cluster_manager.cluster_info.master_node:
                self.stop_engine_manager(spider_name, self.node_info.ip, self.node_info.port)
        else:
            self.transport_manager.send_request(node.ip, node.port, rpc.REQUEST_STOP_ENGINE + spider_name)

    def stop_engine_manager(self, spider_name, ip, port):
        self.cluster_manager.stop_engine_manager(spider_name, nodeinfo.NodeInfo(ip, port))

    def init_engine_manager(self, spider_name, ip, port):
        self.cluster_manager.init_engine_manager(spider_name, nodeinfo.NodeInfo(ip, port))

    def send_request_to_client(self, request, node=None):
        if not node or node == self.node_info:
            self.crawl_client.accept_request(request.spider_name, request)
        else:
            self.transport_manager.send_request(node.ip, node.port,
                                                rpc.REQUEST_SEND_REQUEST + pickle.dumps(request))

    def send_request_to_master(self, request):
        master_node = self.cluster_manager.cluster_info.master_node
        if master_node == self.node_info:
            # #
            # NOTICE must add request first,if none request in waiting list,engine will stop
            self.cluster_manager.add_request(request)
            if hasattr(request, 'source_hash_code'):
                self.cluster_manager.accept_result_of_request(request.spider_name,
                                                              request.node_name,
                                                              request.source_hash_code,
                                                              'ok')
        else:

            self.transport_manager.send_request(master_node.ip, master_node.port,
                                                rpc.RESPONSE_SEND_REQUEST + pickle.dumps(request))

    def send_result_to_master(self, spider_name, node_name, request_hash_code, msg):
        master_node = self.cluster_manager.cluster_info.master_node
        if master_node == self.node_info:
            self.cluster_manager.accept_result_of_request(spider_name,
                                                          node_name,
                                                          request_hash_code,
                                                          msg)
        else:
            self.transport_manager.send_request(master_node.ip,
                                                master_node.port,
                                                rpc.RESPONSE_RESULT_OF_REQUEST + spider_name + ':' + str(
                                                    node_name) + ':' + str(request_hash_code) + ':' + msg)


    def start_a_engine(self, spider_name):
        master_node = self.cluster_manager.cluster_info.master_node
        if self.node_info == master_node:
            self.cluster_manager.start_a_engine(spider_name)
        else:
            self.transport_manager.send_request(master_node.ip, master_node.port,
                                                rpc.REQUEST_START_A_ENGINE + spider_name)

    def get_crawl_status(self):
        master_node = self.cluster_manager.cluster_info.master_node
        if self.node_info == master_node:
            data = dict()
            for spider_name, engine in self.cluster_manager.crawl_server.running_spider_dict.iteritems():
                data[spider_name] = engine.status.make_readable_status()
            return data




