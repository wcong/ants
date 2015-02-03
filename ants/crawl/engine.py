# encoding=utf8
__author__ = 'wcong'
import datetime
import logging

from twisted.python.failure import Failure

import scrapy
from ants.utils import log
import downloader
from ants.utils.extension import ExtensionManager
from ants.signalmanager import SignalManager
from ants.http import Response, Request
from ants import signals
from ants.utils.misc import load_object
import json
from ants.mail import MailSender


class EngineServer():
    def __init__(self, spider, cluster_manager, scheduler):
        self.spider = spider
        self.scheduler = scheduler
        self.cluster_manager = cluster_manager
        self.status = EngineStatusServer()
        self.distribute_index = 0

    def add_request(self, request):
        request.spider_name = self.spider.name
        request.hash_code = hash(
            self.spider.name + str(request) + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.scheduler.push_queue_request(request)
        self.status.waiting_list.append(request)

    def start(self):
        self.cluster_manager.init_all_node(self.spider.name, self.run)

    def run(self):
        for request in self.spider.start_requests():
            self.add_request(request)

    def log_distributed_request(self, request, node_info):
        self.status.waiting_list.remove(request)
        self.status.distribute_dict.setdefault(str(node_info.name), list()).append(request)

    def accept_request_result(self, node_name, request_hash_code, msg):
        node_name = str(node_name)
        del_index = None
        for index, request in enumerate(self.status.distribute_dict[node_name]):
            if request.hash_code == request_hash_code:
                if msg == 'ok':
                    self.status.ok_crawled_dict.setdefault(node_name, list()).append(request)
                else:
                    self.status.not_ok_crawled_dict.setdefault(node_name, list()).append(request)
                del_index = index
                break
        if del_index is not None:
            del self.status.distribute_dict[node_name][del_index]
        if not self.status.waiting_list and self.status.all_node_empty():
            self.cluster_manager.stop_all_node(self.spider.name)

    def stop(self):
        logging.info(self.spider.name + " stop")
        result = self.status.make_readable_status()
        result['end_time'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        dump_file_name = 'logs/' + self.spider.name + '--' + result['start_time'] + '--' + result['end_time'] + '.log'
        body = json.dumps(result, indent=4)
        with open(dump_file_name, 'w') as f:
            f.write(body)
        MailSender().from_settings(self.cluster_manager.settings).send(self.cluster_manager.settings.get('MAIL_LIST'),
                                                                       subject=self.spider.name,
                                                                       body=body)


class EngineClient():
    def __init__(self, spider, node_manager, schedule):
        self.settings = node_manager.settings
        self.node_manager = node_manager
        self.status = EngineStatusClient()
        self.stats = load_object(self.settings['STATS_CLASS'])(self)
        self.spider = spider
        self.scheduler = schedule
        self.signals = SignalManager(self)
        self.downloader = downloader.Downloader(self)
        self.extension_manager = ExtensionManager(self)
        self.scraper = scrapy.Scraper(self, spider)

    def stop(self):
        self.signals.send_catch_log(signal=signals.spider_closed)
        self.signals.disconnect_all()

    def accept_request(self, request):
        if hasattr(request, "callback"):
            callback = getattr(request, "callback")
            if isinstance(callback, str):
                request.callback = getattr(self.spider, callback)
        request.spider_name = self.spider.name
        self.scheduler.push_queue_request(request)
        self.status.waiting_list.append(request)

    def add_request(self, source_request, request):
        request.spider_name = self.spider.name
        request.source_hash_code = source_request.hash_code
        request.node_name = self.node_manager.node_info.name
        if hasattr(request, "callback"):
            callback = getattr(request, "callback")
            if type(callback).__name__ == 'instancemethod':
                request.callback = callback.__name__
        self.node_manager.send_request_to_master(request)

    def send_request_result(self, request, msg='ok'):
        self.status.running_list.remove(request)
        self.status.crawled_num += 1
        self.node_manager.send_result_to_master(self.spider.name,
                                                self.node_manager.node_info.name,
                                                request.hash_code,
                                                msg)

    def crawl_request(self, request):
        self.status.waiting_list.remove(request)
        self.status.running_list.append(request)
        d = self._download(request, self.spider)
        d.addBoth(self._handle_downloader_output, request, self.spider)
        d.addErrback(log.spider_log, spider=self.spider)
        return d

    def _handle_downloader_output(self, response, request, spider):
        assert isinstance(response, (Request, Response, Failure)), response
        # downloader middleware can return requests (for example, redirects)
        if isinstance(response, Request):
            self.add_request(request, response)
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
        return self.download(response, spider) if isinstance(response, Request) else response

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


class EngineStatus(object):
    STATUS_INIT = 0
    STATUS_RUNNING = 1
    STATUS_STOP = 2

    def __init__(self):
        self.status = self.STATUS_INIT
        self.start_time = datetime.datetime.now()


class EngineStatusServer(EngineStatus):
    def __init__(self):
        super(EngineStatusServer, self).__init__()
        self.ok_crawled_dict = dict()
        self.not_ok_crawled_dict = dict()
        self.distribute_dict = dict()
        self.waiting_list = list()

    def all_node_empty(self):
        for v in self.distribute_dict.itervalues():
            if v:
                return False
        return True

    def make_readable_status(self):
        data = dict()
        data['start_time'] = self.start_time.strftime('%Y-%m-%dT%H:%M:%S')
        data['ok_crawled_dict'] = {k: len(v) for k, v in self.ok_crawled_dict.iteritems()}
        data['not_ok_crawled_dict'] = {k: len(v) for k, v in self.not_ok_crawled_dict.iteritems()}
        data['distribute_dict'] = {k: len(v) for k, v in self.distribute_dict.iteritems()}
        data['waiting_list'] = len(self.waiting_list)
        return data


class EngineStatusClient(EngineStatus):
    def __init__(self):
        super(EngineStatusClient, self).__init__()
        self.crawled_num = 0
        self.running_list = list()
        self.waiting_list = list()

