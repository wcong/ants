__author__ = 'wcong'

from ants import spidermanager
import engine
from ants.crawl import scheduler

'''
crawl server and client
'''


class CrawlServer():
    '''
    cluster get a crawl job , distribute it to all the node
    '''

    def __init__(self, cluster):
        self.setting = cluster.setting
        self.cluster = cluster
        self.schedule = scheduler.SchedulerServer(cluster.setting)
        self.spider_manager = spidermanager.SpiderManager(cluster.node_manager.setting.get('SPIDER_MODULES'))
        self.running_spider_dict = dict()
        self.init_spider_dict = dict()
        self.idle_spider_dict = dict()

    def init_spider_job(self, spider_name):
        if spider_name in self.running_spider_dict:
            raise RunningJobException()
        spider = self.spider_manager.create(spider_name)
        crawl_engine = engine.EngineServer(spider, self.cluster)
        self.running_spider_dict[spider_name] = crawl_engine

    def run(self, spider_name):
        self.running_spider_dict[spider_name].run()

    def accept_request(self, spider_name, request):
        self.running_spider_dict[spider_name].add_request(request)


class CrawlClient():
    '''
    nodes init a spider,and listen the request job,get a job execute it and return result
    '''

    def __init__(self, node_manager):
        self.node_manager = node_manager
        self.spider_manager = spidermanager.SpiderManager(node_manager.setting.get('SPIDER_MODULES'))
        self.schedule = scheduler.SchedulerClient(node_manager.setting)
        self.running_spider_dict = dict()

    def spider_list(self):
        return self.spider_manager.list()

    def init_engine(self, spider_name):
        if spider_name in self.running_spider_dict:
            raise RunningJobException()
        spider = self.spider_manager.create(spider_name)
        crawl_engine = engine.EngineClient(spider, self.node_manager, self.schedule)
        self.running_spider_dict[spider_name] = crawl_engine

    def run(self, spider_name):
        self.running_spider_dict[spider_name].run()

    def accept_request(self, spider_name, request):
        self.running_spider_dict[spider_name].add_request(request)

    def is_idle(self, spider_name):
        return True if self.running_spider_dict[spider_name].status.status == engine.EngineStatus.STATUS_STOP else False


class RunningJobException(Exception):
    '''
    job is running
    '''



