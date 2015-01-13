import json


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