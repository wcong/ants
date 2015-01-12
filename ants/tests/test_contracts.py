from unittest import TextTestResult

from twisted.trial import unittest

from ants.spider import Spider
from ants.http import Request
from ants.item import Item, Field
from ants.contracts import ContractsManager
from ants.contracts.default import (
    UrlContract,
    ReturnsContract,
    ScrapesContract,
)


class TestItem(Item):
    name = Field()
    url = Field()


class ResponseMock(object):
    url = 'http://ants.org'


class TestSpider(Spider):
    name = 'demo_spider'

    def returns_request(self, response):
        """ method which returns request
        @url http://ants.org
        @returns requests 1
        """
        return Request('http://ants.org', callback=self.returns_item)

    def returns_item(self, response):
        """ method which returns item
        @url http://ants.org
        @returns items 1 1
        """
        return TestItem(url=response.url)

    def returns_fail(self, response):
        """ method which returns item
        @url http://ants.org
        @returns items 0 0
        """
        return TestItem(url=response.url)

    def scrapes_item_ok(self, response):
        """ returns item with name and url
        @url http://ants.org
        @returns items 1 1
        @scrapes name url
        """
        return TestItem(name='test', url=response.url)

    def scrapes_item_fail(self, response):
        """ returns item with no name
        @url http://ants.org
        @returns items 1 1
        @scrapes name url
        """
        return TestItem(url=response.url)

    def parse_no_url(self, response):
        """ method with no url
        @returns items 1 1
        """
        pass


class ContractsManagerTest(unittest.TestCase):
    contracts = [UrlContract, ReturnsContract, ScrapesContract]

    def setUp(self):
        self.conman = ContractsManager(self.contracts)
        self.results = TextTestResult(stream=None, descriptions=False, verbosity=0)

    def should_succeed(self):
        self.assertFalse(self.results.failures)
        self.assertFalse(self.results.errors)

    def should_fail(self):
        self.assertTrue(self.results.failures)
        self.assertFalse(self.results.errors)

    def test_contracts(self):
        spider = TestSpider()

        # extract contracts correctly
        contracts = self.conman.extract_contracts(spider.returns_request)
        self.assertEqual(len(contracts), 2)
        self.assertEqual(frozenset(type(x) for x in contracts),
            frozenset([UrlContract, ReturnsContract]))

        # returns request for valid method
        request = self.conman.from_method(spider.returns_request, self.results)
        self.assertNotEqual(request, None)

        # no request for missing url
        request = self.conman.from_method(spider.parse_no_url, self.results)
        self.assertEqual(request, None)

    def test_returns(self):
        spider = TestSpider()
        response = ResponseMock()

        # returns_item
        request = self.conman.from_method(spider.returns_item, self.results)
        request.callback(response)
        self.should_succeed()

        # returns_request
        request = self.conman.from_method(spider.returns_request, self.results)
        request.callback(response)
        self.should_succeed()

        # returns_fail
        request = self.conman.from_method(spider.returns_fail, self.results)
        request.callback(response)
        self.should_fail()

    def test_scrapes(self):
        spider = TestSpider()
        response = ResponseMock()

        # scrapes_item_ok
        request = self.conman.from_method(spider.scrapes_item_ok, self.results)
        request.callback(response)
        self.should_succeed()

        # scrapes_item_fail
        request = self.conman.from_method(spider.scrapes_item_fail,
                self.results)
        request.callback(response)
        self.should_fail()
