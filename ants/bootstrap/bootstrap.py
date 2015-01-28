#!/usr/bin/env python
# encoding=utf8
__author__ = 'wcong'
import sys
from twisted.internet import reactor
from ants.node import node
from ants import settings
from conf import settings as project_settings
import logging
import argparse

'''
what we do
start the node
let the node do what he need to do
'''

logging.basicConfig(format="[%(asctime)s %(module)s %(lineno)d]%(levelname)s:%(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

parser = argparse.ArgumentParser(description='ants -- scale crawler')
parser.add_argument('-tcp_port', help='transport port', type=int, dest='tcp_port')
parser.add_argument('-http_port', help='http port', type=int, dest='http_port')


class Bootstrap():
    def __init__(self, args):
        logging.info("do not panic,it is shipping")
        self.setting = settings.Settings()
        self.setting.setmodule(project_settings)
        if args:
            cmd_args = parser.parse_args(args)
            if cmd_args.tcp_port:
                self.setting.set('TRANSPORT_PORT', cmd_args.tcp_port)
            if cmd_args.http_port:
                self.setting.set('HTTP_PORT', cmd_args.http_port)


    # #
    # we init almost everything in node manager
    def start(self):
        node_manager = node.NodeManager(self.setting)
        node_manager.start()
        reactor.run()


if __name__ == '__main__':
    Bootstrap(sys.argv[1:]).start()

