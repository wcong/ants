__author__ = 'wcong'

from ants.webservice import webservice
from ants.cluster import cluster
from ants.crawl import crawl
from twisted.internet import reactor
import unittest
from ants import settings


class WebServiceTest(unittest.TestCase):
    def test(self):
        cluster_info = cluster.ClusterInfo(name='test')
        setting = settings.Settings()
        crawl_manager = crawl.CrawlManager(setting, cluster_info)
        web_service_management = webservice.WebServiceManager(8080, cluster_info, crawl_manager)
        web_service_management.start()
        reactor.run()


if __name__ == '__main__':
    unittest.main()