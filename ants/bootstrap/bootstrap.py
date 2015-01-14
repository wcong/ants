# encoding=utf8
__author__ = 'wcong'
from ants import log
import sys
from twisted.internet import reactor
from ants.node import node
from ants import settings
import logging

'''
what we do
start the node
let the node do what he need to do
'''


class Bootstrap():
    def __init__(self, *args, **kwargs):
        log.msg("do not panic,it is shipping")

    '''
    we init almost everything in node manager
    '''

    def start(self):
        logging.basicConfig(format="[%(asctime)s %(name)s %(module)s %(lineno)d]%(levelname)s:%(message)s",
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO)
        setting = settings.Settings()
        node_manager = node.NodeManager(setting)
        node_manager.start()
        log.start_from_settings(setting)
        reactor.run()


if __name__ == '__main__':
    Bootstrap(sys.argv).start()

