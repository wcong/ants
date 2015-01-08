__author__ = 'wcong'

from scrapy import management


'''
### manage crawl
*   scan crawl list by path
*   start a crawl job and start a monitor of crawl
'''


class CrawlManagement(management.Management):
    def __init__(self, cluster_info):
        self.cluster_info = cluster_info

    def start(self):
        pass

    def stop(self):
        pass

    def scan_crawl_list(self):
