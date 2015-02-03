__author__ = 'wcong'
MULTICAST_ENABLED = False
NODE_LIST = ('127.0.0.1', 9300,
             '127.0.0.1', 8300)
MASTER = ['127.0.0.1', 9300]
MAIL_LIST=['cong.wang@tqmall.com']
MAIL_HOST='smtp.126.com'
MAIL_FROM='tqmall2014@126.com'
MAIL_USER='tqmall2014@126.com'
MAIL_PASS='tqdk2014'

ITEM_PIPELINES = {
    # 'antsext.db-pipe-line.CrawlPipeline': 800
}