__author__ = 'wcong'

from scrapy.webservice import webservice
from scrapy.cluster import clusterinfo
from twisted.internet import reactor
import unittest


class WebServiceTest(unittest.TestCase):
    def test(self):
        web_service_management = webservice.WebServiceManagement(8080, clusterinfo.ClusterInfo(name='test'))
        web_service_management.start()
        reactor.run()


if __name__ == '__main__':
    unittest.main()