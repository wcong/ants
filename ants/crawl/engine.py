# encoding=utf8
__author__ = 'wcong'
import datetime
import scrapy
from ants.utils import log
import logging
import downloader
from ants.extension import ExtensionManager
from ants.signalmanager import SignalManager
from ants.http import Response, Request
from ants import signals
from twisted.python.failure import Failure
from ants.utils.misc import load_object


class EngineServer():
    def __init__(self, spider, cluster_manager, scheduler):
        self.spider = spider
        self.scheduler = scheduler
        self.cluster_manager = cluster_manager
        self.status = EngineStatus()
        self.distribute_index = 0

    def add_request(self, request):
        request.spider_name = self.spider.name
        self.scheduler.push_queue_request(request)

    def pop_request(self):
        return self.scheduler.next_request()

    def start(self):
        self.cluster_manager.init_all_node(self.spider.name, self.run)

    def run(self):
        for request in self.spider.start_requests():
            request.spider_name = self.spider.name
            self.scheduler.push_queue_request(request)

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
        self.settings = node_manager.settings
        self.node_manager = node_manager
        self.status = EngineStatus()
        self.stats = load_object(self.settings['STATS_CLASS'])(self)
        self.spider = spider
        self.scheduler = schedule
        self.signals = SignalManager(self)
        self.downloader = downloader.Downloader(self)
        self.extension_manager = ExtensionManager(self)
        self.scraper = scrapy.Scraper(self, spider)

    def accept_request(self, request):
        request.spider_name = self.spider.name
        self.scheduler.push_queue_request(request)

    def add_request(self, request):
        request.spider_name = self.spider.name
        self.node_manager.send_request_to_master(request)

    def crawl_request(self, request):
        d = self._download(request, self.spider)
        d.addBoth(self._handle_downloader_output, request, self.spider)
        d.addErrback(log.spider_log, spider=self.spider)
        return d

    def _handle_downloader_output(self, response, request, spider):
        assert isinstance(response, (Request, Response, Failure)), response
        # downloader middleware can return requests (for example, redirects)
        if isinstance(response, Request):
            self.add_request(response)
            return
        # response is a Response or Failure
        d = self.scraper.enqueue_scrape(response, request, spider)
        d.addErrback(log.spider_log, spider=spider)
        return d

    def download(self, request, spider):
        d = self._download(request, spider)
        d.addBoth(self._downloaded, request, spider)
        return d

    def _downloaded(self, response, request, spider):
        return self.download(response, spider) \
            if isinstance(response, Request) else response

    def _download(self, request, spider):
        def _on_success(response):
            assert isinstance(response, (Response, Request))
            if isinstance(response, Response):
                response.request = request  # tie request to response received
                logging.info(spider.name + ':' + 'crawled url:' + response.url)
                self.signals.send_catch_log(signal=signals.response_received,
                                            response=response, request=request, spider=spider)
            return response

        dwld = self.downloader.fetch(request, spider)
        dwld.addCallbacks(_on_success)
        return dwld


class EngineStatus():
    STATUS_INIT = 0
    STATUS_RUNNING = 1
    STATUS_STOP = 2

    def __init__(self):
        self.status = self.STATUS_INIT
        self.start_time = datetime.datetime.now()