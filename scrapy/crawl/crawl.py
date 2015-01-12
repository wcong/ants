__author__ = 'wcong'

from scrapy import manager
from scrapy import spidermanager
from scrapy import log
from scrapy import crawler
import datetime
from scrapy.core.engine import ExecutionEngine

'''
### manage crawl
*   scan crawl list by path
*   start a crawl job and start a monitor of crawl
*   distribute request

'''

'''
### start a spider
*   notice all node that we should start a spider
*   node accept the start request,and load the spider ,notice the master ,then wait to crawl request
*   master found all node ready ,start to distribute the request
'''

'''
### manager spider
*   request unique key
*   accept a request and crawl it
*   finish a request notice master
*
'''


class CrawlManager(manager.Manager):
    def __init__(self, setting, node_manager):
        self.setting = setting
        self.spider_manager = spidermanager.SpiderManager(setting.get('SPIDER_MODULES'))
        self.node_manager = node_manager
        self.crawler_process = crawler.CrawlerProcess(self.setting)
        self.crawler = self.crawler_process.create_crawler("main")
        self.running_crawl_job_dict = dict()
        self.end_crawl_job_list = list()


    def start(self):
        pass

    def stop(self):
        pass

    def spider_list(self):
        return self.spider_manager.list()

    def start_crawl(self, spider_name):
        spider = self.crawler.spiders.create(spider_name)
        self.crawler.crawl(spider)
        self.crawler_process.start()

    def init_crawl(self, spider_name):
        log.msg(spider_name)
        if spider_name in self.running_crawl_job_dict:
            raise RunningJobException()
        spider = self.crawler.spiders.create(spider_name)
        crawl_job = CrawlJob(spider_name, CrawlStatus.init, spider)
        self.running_crawl_job_dict[spider_name] = crawl_job

    def crawl_by_request(self, request, spider_name):
        self.crawler.engine.unpause()
        self.crawler.engine.slot.scheduler.enqueue_request(request)


class CrawlJob():
    def __init__(self, crawl_name, status, spider):
        self.crawl_name = crawl_name
        self.status = status
        self.spider = spider
        self.start_time = datetime.datetime.now()
        self.future_request_list = list()
        self.running_request_list = list()
        self.stop_request_list = list()


class CrawlScheduler():
    def __init__(self, crawl_job, setting):
        self.setting = setting
        self.crawl_job = crawl_job
        self.engine = ExecutionEngine(self, self._spider_closed)

    def run(self):
        '''
        '''


class CrawlStatus():
    init = 0
    start = 1
    stop = 2


class RunningJobException(Exception):
    '''
    job is running
    '''



