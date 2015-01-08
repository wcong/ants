# encoding=utf8
__author__ = 'wcong'
import scrapy


class SimpleTest(scrapy.Spider):
    name = "simple_test"

    start_urls = [
        'http://www.baidu.com'
    ]

    def parse(self, response):
        yield scrapy.Request('http://tieba.baidu.com', callback=self.parse_a)

    def parse_a(self, response):
        yield scrapy.Request('http://tieba.baidu.com', callback=self.parse_a)
        # return response
