__author__ = 'wcong'

from scrapy import manager
from scrapy import spidermanager
from scrapy import log
from scrapy import crawler
import datetime

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
        spider = self.crawler.spiders.create(spider_name)
        self.crawler.crawl(spider)
        self.crawler_process.start()
        self.crawler.engine.pause()

    def crawl_by_request(self, request, spider_name):
        self.crawler.engine.unpause()
        self.crawler.engine.slot.scheduler.enqueue_request(request)




class ClassJobs():
    def __init__(self, crawl_name, status):
        self.crawl_name = crawl_name
        self.status = status
        self.start_time = datetime.datetime.now()

