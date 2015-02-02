__author__ = 'wcong'
from twisted.enterprise import adbapi
from MySQLdb import cursors
import dbitem


class CrawlPipeline(object):
    def open_spider(self, spider):
        self.db_pool = adbapi.ConnectionPool('MySQLdb',
                                             db='crawl',
                                             user='crawl_all',
                                             passwd='crawl.tqmall2014',
                                             host='121.199.42.91',
                                             cursorclass=cursors.DictCursor,
                                             charset='utf8',
        )

    def process_item(self, item, spider):
        if isinstance(item, dbitem.DbItem):
            self.db_pool.runQuery(item['query']).addCallback(item['callback'])
        return item

    def close_spider(self, spider):
        self.db_pool.close()