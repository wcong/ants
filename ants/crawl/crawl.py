__author__ = 'wcong'

from ants import spidermanager
import engine
from ants.crawl import scheduler
from twisted.internet import reactor
from ants import log

'''
crawl server and client
'''


class CrawlServer():
    '''
    cluster get a crawl job
    distribute it to all the node
    '''
    STATUS_RUNNING = 1
    STATUS_STOP = 2

    def __init__(self, cluster_manager):
        self.settings = cluster_manager.settings
        self.cluster_manager = cluster_manager
        self.status = self.STATUS_STOP
        self.scheduler = scheduler.SchedulerServer(cluster_manager.settings)
        self.spider_manager = spidermanager.SpiderManager(cluster_manager.node_manager.settings.get('SPIDER_MODULES'))
        self.running_spider_dict = dict()
        self.init_spider_dict = dict()
        self.idle_spider_dict = dict()
        self.distribute_index = 0

    def init_spider_job(self, spider_name):
        if spider_name in self.running_spider_dict:
            raise RunningJobException()
        spider = self.spider_manager.create(spider_name)
        crawl_engine = engine.EngineServer(spider, self.cluster_manager)
        self.running_spider_dict[spider_name] = crawl_engine

    def run_engine(self, spider_name):
        del self.init_spider_dict[spider_name]
        self.running_spider_dict[spider_name].run()
        if self.status == self.STATUS_STOP:
            self.status = self.STATUS_RUNNING
            self.distribute()

    def stop_engine(self, spider_name):
        self.running_spider_dict[spider_name].stop()
        del self.running_spider_dict[spider_name]
        if not self.running_spider_dict:
            self.status = self.STATUS_STOP


    def distribute(self):
        if self.status == self.STATUS_STOP:
            return
        request = self.scheduler.next_request()
        if request:
            if self.distribute_index > len(self.cluster_manager.cluster_info.node_list):
                self.distribute_index = 0
            self.cluster_manager.node_manager.send_request_to_client(request)
        reactor.callLater(0, self)

    def __call__(self, *args, **kwargs):
        self.distribute()

    def accept_request(self, spider_name, request):
        self.running_spider_dict[spider_name].add_request(request)


class CrawlClient():
    '''
    nodes init a spider,and listen the request job
    get a job execute it and return result
    '''

    STATUS_RUNNING = 1
    STATUS_STOP = 2

    def __init__(self, node_manager):
        self.status = self.STATUS_STOP
        self.node_manager = node_manager
        self.spider_manager = spidermanager.SpiderManager(node_manager.settings.get('SPIDER_MODULES'))
        self.scheduler = scheduler.SchedulerClient(node_manager.settings)
        self.running_spider_dict = dict()

    def spider_list(self):
        return self.spider_manager.list()

    def init_engine(self, spider_name):
        if spider_name in self.running_spider_dict:
            raise RunningJobException()
        spider = self.spider_manager.create(spider_name)
        crawl_engine = engine.EngineClient(spider, self.node_manager, self.scheduler)
        self.running_spider_dict[spider_name] = crawl_engine

    def run(self, spider_name):
        if self.status == self.STATUS_STOP:
            self.status = self.STATUS_RUNNING
            log.start_from_settings(self.node_manager.settings)
            self.distribute()

    def __call__(self, *args, **kwargs):
        self.distribute()

    def distribute(self):
        request = self.scheduler.next_request()
        if request:
            self.running_spider_dict[request.spider_name].crawl_request(request)
        reactor.callLater(0, self)

    def accept_request(self, spider_name, request):
        self.running_spider_dict[spider_name].add_request(request)


class RunningJobException(Exception):
    '''
    job is running
    '''



