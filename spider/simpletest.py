# encoding=utf8
__author__ = 'wcong'
import ants


class SimpleTest(ants.Spider):
    name = "simple_test"

    start_urls = [
        'http://www.baidu.com'
    ]

    def parse(self, response):
        yield ants.Request('http://tieba.baidu.com', callback=self.parse_a)

    def parse_a(self, response):
        yield ants.Request('http://tieba.baidu.com', callback=self.parse_a)
        # return response
