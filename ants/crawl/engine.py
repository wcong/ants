# encoding=utf8
__author__ = 'wcong'
import datetime
import scheduler
import scrapy
from twisted.internet import reactor
from ants.core import downloader


class EngineServer():
    def __init__(self, spider, cluster):
        self.spider = spider
        self.cluster = cluster
        self.status = EngineStatus()
        self.scheduler = scheduler.SchedulerServer(cluster.setting)
        self.distribute_index = 0

    def add_request(self, request):
        request.spider_name = self.spider.name
        self.scheduler.push_queue_request(request)

    def pop_request(self):
        return self.scheduler.next_request()

    def start(self):
        self.cluster.init_all_node(self.spider.name, self.run)

    def run(self):
        for request in self.spider.start_requests():
            request.spider_name = self.spider.name
            self.scheduler.push_queue_request(request)
        self.distribute()

    def distribute(self):
        if self.is_idle():
            self.cluster.is_all_idle(self.spider.name, self.stop)
            return
        request = self.scheduler.next_request()
        if self.distribute_index > len(self.cluster.cluster_info.node_list):
            self.distribute_index = 0
        self.cluster.node_manager.send_request(request)
        reactor.callLater(0, self)

    def __call__(self, *args, **kwargs):
        self.distribute()

    def stop(self):
        '''
        :return:
        '''

    def is_idle(self):
        '''
        :return:
        '''


class EngineClient():
    def __init__(self, spider, node_manager, schedule):
        self.setting = node_manager.setting
        self.node_manager = node_manager
        self.status = EngineStatus()
        self.spider = spider
        self.scheduler = schedule
        self.scraper = scrapy.Scraper(self)
        self.downloader = downloader.Downloader()


    def run(self):
        if self.is_idle():
            reactor.callLater(0, self)


    def __call__(self, *args, **kwargs):
        self.run()

    def add_request(self, request):
        request.spider_name = self.spider.name
        self.scheduler.push_queue_request(request)

    def pop_request(self):
        return self.scheduler.next_request()


class EngineStatus():
    STATUS_INIT = 0
    STATUS_RUNNING = 1
    STATUS_STOP = 2

    def __init__(self):
        self.status = self.STATUS_INIT
        self.start_time = datetime.datetime.now()



