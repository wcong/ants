'''
what a cluster should have
'''
__author__ = 'wcong'
from ants import log
from ants import manager
from ants.node import nodeinfo
from ants.crawl import crawl
from ants.crawl import scheduler


class ClusterManager(manager.Manager):
    def __init__(self, node_manager):
        self.settings = node_manager.settings
        self.node_manager = node_manager
        self.cluster_info = ClusterInfo(self.settings, node_manager.node_info)
        self.crawl_server = crawl.CrawlServer(self)

    def start(self):
        pass

    def stop(self):
        pass

    def find_node(self, addr, data):
        data = data.strip().split(':')
        name = data[0]
        if name != self.cluster_info.name:
            log.msg("name not the same,mine:" + self.cluster_info.name + ';accept:' + name + ';ignore')
            return
        ip = addr[0]
        port = data[1]
        node_info = nodeinfo.NodeInfo(ip, port)
        if self.cluster_info.contain_node(node_info):
            log.msg("we already have the node,ip:" + ip + ';port:' + port)
            return
        self.node_manager.transport_manager.run_client(ip, port)


    def add_request(self, request):
        self.crawl_server.accept_request(request.spider_name, request)

    def add_node(self, ip, port):
        log.msg("add ip:" + ip + ';port:' + port + ';node to cluster')
        self.cluster_info.node_list.append(nodeinfo.NodeInfo(ip, port))

    def is_all_idle(self, spider_name):
        self.crawl_server.idle_spider_dict[spider_name] = self.cluster_info.node_list
        for node in self.cluster_info.node_list:
            self.node_manager.is_idle(spider_name, node)

    def idle_engine_manager(self, spider_name, node_info):
        self.crawl_server.idle_spider_dict[spider_name].remove(node_info)
        if len(self.crawl_server.idle_spider_dict[spider_name]) == 0:
            self.crawl_server.stop_engine(spider_name)

    def init_all_node(self, spider_name):
        self.crawl_server.init_spider_dict[spider_name] = self.cluster_info.node_list
        for node in self.cluster_info.node_list:
            self.node_manager.init_engine(spider_name, node)

    def init_engine_manager(self, spider_name, inited_node_info):
        self.crawl_server.init_spider_dict[spider_name].remove(inited_node_info)
        if len(self.crawl_server.init_spider_dict[spider_name]) == 0:
            self.crawl_server.run_engine(spider_name)

    def start_a_engine(self, spider_name):
        self.crawl_server.init_spider_job(spider_name)
        self.init_all_node(spider_name)


class ClusterInfo():
    def __init__(self, setting, local_node):
        self.setting = setting
        self.name = self.setting.get('CLUSTER_NAME')
        self.local_node = local_node
        self.node_list = list()
        self.node_list.append(local_node)
        self.master_node = local_node

    def append_node(self, node):
        self.node_list.append(node)
        self.elect_master()

    def elect_master(self):
        master_node = self.node_list[0]
        for had_node in self.node_list:
            if had_node.name < master_node.name:
                master_node = had_node
        if master_node != self.master_node:
            self.master_node = master_node

    def contain_node(self, new_node):
        for old_node in self.node_list:
            if old_node == new_node:
                return True
        else:
            return False

    def change_master_node(self, node):
        self.master_node = node





