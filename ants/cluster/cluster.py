'''
what a cluster should have
'''
from ants.utils import manager

__author__ = 'wcong'
import logging
from ants.node import nodeinfo
from ants.crawl import crawl


class ClusterManager(manager.Manager):
    def __init__(self, node_manager):
        self.settings = node_manager.settings
        self.node_manager = node_manager
        self.cluster_info = ClusterInfo(self.settings, node_manager.node_info)
        self.crawl_server = crawl.CrawlServer(self)

    def start(self):
        node_list = self.settings.get('NODE_LIST')
        if node_list:
            i = 0
            while i < len(node_list):
                ip = node_list[i]
                if ip == '127.0.0.1':
                    ip = self.node_manager.node_info.ip
                self.node_manager.connect_to_node(ip, node_list[i + 1])
                i += 2

    def stop(self):
        pass

    def find_node(self, addr, data):
        data = data.strip().split(':')
        name = data[0]
        if name != self.cluster_info.name:
            logging.info("name not the same,mine:" + self.cluster_info.name + ';accept:' + name + ';ignore')
            return
        ip = addr[0]
        port = data[1]
        self.node_manager.connect_to_node(ip, port)

    def add_request(self, request):
        self.crawl_server.accept_request(request.spider_name, request)

    def add_node(self, ip, port):
        node_info = nodeinfo.NodeInfo(ip, port)
        if self.cluster_info.contain_node(node_info):
            logging.info("we already have the node,ip:" + ip + ';port:' + str(port))
            return
        logging.info("add ip:" + ip + ';port:' + str(port) + ';node to cluster')
        self.cluster_info.append_node(nodeinfo.NodeInfo(ip, port))

    def init_all_node(self, spider_name):
        self.crawl_server.init_init_job_dict(spider_name, self.cluster_info.node_list)
        for node in self.cluster_info.node_list:
            self.node_manager.init_engine(spider_name, node)

    def init_engine_manager(self, spider_name, inited_node_info):
        self.crawl_server.remove_init_node(spider_name, inited_node_info)
        if len(self.crawl_server.init_spider_dict[spider_name]) == 0:
            self.crawl_server.run_engine(spider_name)

    def start_a_engine(self, spider_name):
        self.crawl_server.init_spider_job(spider_name)
        self.init_all_node(spider_name)

    def accept_result_of_request(self, spider_name, node_name, request_code, msg):
        self.crawl_server.accept_crawl_result(spider_name, node_name, request_code, msg)

    def stop_all_node(self, spider_name):
        self.crawl_server.init_stop_job_dict(spider_name, self.cluster_info.node_list)
        for node in self.cluster_info.node_list:
            self.node_manager.stop_engine(spider_name, node)

    def stop_engine_manager(self, spider_name, inited_node_info):
        self.crawl_server.remove_stop_job_dict(spider_name, inited_node_info)
        if not self.crawl_server.stop_spider_dict[spider_name]:
            self.crawl_server.stop_engine(spider_name)


class ClusterInfo():
    def __init__(self, setting, local_node):
        self.name = setting.get('CLUSTER_NAME')
        self.setting_master = setting.get('MASTER')
        if self.setting_master:
            if self.setting_master[0] == '127.0.0.1':
                self.setting_master[0] = local_node.ip
        self.local_node = local_node
        self.node_list = list()
        self.node_list.append(local_node)
        self.master_node = local_node

    def append_node(self, node):
        self.node_list.append(node)
        self.elect_master()

    def elect_master(self):
        if self.setting_master:
            self.choose_setting_master()
            return
        master_node = self.node_list[0]
        for had_node in self.node_list:
            if had_node.name < master_node.name:
                master_node = had_node
        if master_node != self.master_node:
            logging.info("elect node:ip:" + master_node.ip + ';port:' + str(master_node.port) + ';master')
            self.master_node = master_node

    def choose_setting_master(self):
        if self.master_node.ip == self.setting_master[0] and self.master_node.port == self.setting_master[1]:
            return
        for had_node in self.node_list:
            if had_node.ip == self.setting_master[0] and had_node.port == self.setting_master[1]:
                self.master_node = had_node
                break

    def contain_node(self, new_node):
        for old_node in self.node_list:
            if old_node == new_node:
                return True
        else:
            return False

    def change_master_node(self, node):
        self.master_node = node

    def get_node_by_name(self, name):
        for node in self.node_list:
            if node.name == name:
                return node
