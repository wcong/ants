from unittest import TestCase

from ants.http import Response, Request
from ants.spider import Spider
from ants.contrib.spidermiddleware.offsite import OffsiteMiddleware
from ants.utils.test import get_crawler

from urlparse import urlparse

class TestOffsiteMiddleware(TestCase):

    def setUp(self):
        self.spider = self._get_spider()
        crawler = get_crawler()
        self.mw = OffsiteMiddleware.from_crawler(crawler)
        self.mw.spider_opened(self.spider)

    def _get_spider(self):
        return Spider('foo', allowed_domains=['scrapytest.org', 'ants.org'])

    def test_process_spider_output(self):
        res = Response('http://scrapytest.org')

        onsite_reqs = [Request('http://scrapytest.org/1'),
                       Request('http://ants.org/1'),
                       Request('http://sub.ants.org/1'),
                       Request('http://offsite.tld/letmepass', dont_filter=True)]
        offsite_reqs = [Request('http://scrapy2.org'),
                       Request('http://offsite.tld/'),
                       Request('http://offsite.tld/scrapytest.org'),
                       Request('http://offsite.tld/rogue.scrapytest.org'),
                       Request('http://rogue.scrapytest.org.haha.com'),
                       Request('http://roguescrapytest.org')]
        reqs = onsite_reqs + offsite_reqs

        out = list(self.mw.process_spider_output(res, reqs, self.spider))
        self.assertEquals(out, onsite_reqs)


class TestOffsiteMiddleware2(TestOffsiteMiddleware):

    def _get_spider(self):
        return Spider('foo', allowed_domains=None)

    def test_process_spider_output(self):
        res = Response('http://scrapytest.org')
        reqs = [Request('http://a.com/b.html'), Request('http://b.com/1')]
        out = list(self.mw.process_spider_output(res, reqs, self.spider))
        self.assertEquals(out, reqs)

class TestOffsiteMiddleware3(TestOffsiteMiddleware2):

    def _get_spider(self):
        return Spider('foo')


class TestOffsiteMiddleware4(TestOffsiteMiddleware3):

    def _get_spider(self):
      bad_hostname = urlparse('http:////scrapytest.org').hostname
      return Spider('foo', allowed_domains=['scrapytest.org', None, bad_hostname])

    def test_process_spider_output(self):
      res = Response('http://scrapytest.org')
      reqs = [Request('http://scrapytest.org/1')]
      out = list(self.mw.process_spider_output(res, reqs, self.spider))
      self.assertEquals(out, reqs)
