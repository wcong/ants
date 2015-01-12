__author__ = 'wcong'
import unittest
from ants.crawl import crawl
from ants import settings
from ants import log
from twisted.internet import reactor


class CrawlTest(unittest.TestCase):
    def test(self):
        setting = settings.Settings()
        crawl_manager = crawl.CrawlManager(setting, None)
        crawl_manager.start_crawl("simple_test")
        reactor.run()


if __name__ == '__main__':
    unittest.main()
