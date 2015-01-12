'''
what a cluster should have
'''
__author__ = 'wcong'
from ants import log
from ants import manager
from ants.node import node


class ClusterManager(manager.Manager):
    def __init__(self, setting, local_node, node_manager):
        self.setting = setting
        self.node_manager = node_manager
        self.cluster_info = ClusterInfo(setting, local_node)

    def start(self):
        pass

    def stop(self):
        pass

    def start_a_crawl(self, spider_name):
        log.msg(spider_name)

    def find_node(self, addr, data):
        data = data.strip().split(':')
        name = data[0]
        if name != self.cluster_info.name:
            log.msg("name not the same,mine:" + self.cluster_info.name + ';accept:' + name + ';ignore')
            return
        ip = addr[0]
        port = data[1]
        node_info = node.NodeInfo(ip, port)
        if self.cluster_info.contain_node(node_info):
            log.msg("we already have the node,ip:" + ip + ';port:' + port)
            return
        self.node_manager.transport_manager.run_client(ip, port)

    def add_node(self, ip, port):
        log.msg("add ip:" + ip + ';port:' + port + ';node to cluster')
        self.cluster_info.node_list.append(node.NodeInfo(ip, port))


class ClusterInfo():
    def __init__(self, setting, local_node):
        self.setting = setting
        self.name = self.setting.get('CLUSTER_NAME')
        self.local_node = local_node
        self.node_list = list()
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





