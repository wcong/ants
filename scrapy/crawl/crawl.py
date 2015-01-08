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
'''


class CrawlManager(manager.Manager):
    def __init__(self, setting, cluster_info):
        self.cluster_info = cluster_info
        self.setting = setting
        self.spider_manager = spidermanager.SpiderManager(setting.get('SPIDER_MODULES'))
        self.crawler_process = crawler.CrawlerProcess(self.setting)
        self.crawler = self.crawler_process.create_crawler("main")

    def start(self):
        pass

    def stop(self):
        pass

    def spider_list(self):
        return self.spider_manager.list()

    def start_crawl(self, spider_name):
        log.msg(spider_name)
        spider = self.crawler.spiders.create(spider_name)
        self.crawler.crawl(spider)
        self.crawler_process.start()


class ClassJobs():
    def __init__(self, crawl_name, status):
        self.crawl_name = crawl_name
        self.status = status
        self.start_time = datetime.datetime.now()

