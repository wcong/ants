# encoding=utf8
__author__ = 'wcong'
'''
control crawl and get crawl status
'''

from twisted.web import server, resource
from twisted.internet import reactor
from scrapy import manager, log
from scrapy.utils.jsonextends import JSON
import datetime
import json


class WebServiceManager(manager.Manager):
    def __init__(self, port, cluster_info, crawl_manager):
        self.port = port
        self.cluster_info = cluster_info
        self.start_time = datetime.datetime.now()
        self.crawl_manager = crawl_manager
        self.__init_service()

    def __init_service(self):
        resource = Service(self.cluster_info)
        resource.putChild('node', NodeService(self.cluster_info))
        resource.putChild('spider_list', SpiderListService(self.cluster_info, self.crawl_manager))
        resource.putChild('crawl', CrawlService(self.cluster_info, self.crawl_manager))
        resource.putChild('crawl_status', CrawlStatusService(self.cluster_info, self.crawl_manager))
        self.service = server.Site(resource)

    def start(self):
        reactor.listenTCP(self.port, self.service)

    def stop(self):
        now = datetime.datetime.now()
        log.msg(
            "start in :" + self.start_time.strftime("%Y-%m-%d %H:%M:%S") + ';end:' + now.strftime("%Y-%m-%d %H:%M:%S"))


class Service(resource.Resource):
    def __init__(self, cluster_info):
        resource.Resource.__init__(self)
        self.cluster_info = cluster_info

    def getChild(self, path, request):
        if path == '':
            return self
        return resource.Resource.getChild(self, path, request)

    def render_GET(self, request):
        data = dict()
        data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['greeting'] = 'do not panic'
        data['message'] = 'for crawl'
        return json.dumps(data)


class NodeService(Service):
    def render_GET(self, request):
        return json.dumps(self.cluster_info, cls=JSON)


class SpiderListService(Service):
    def __init__(self, cluster_info, crawl_manager):
        Service.__init__(self, cluster_info)
        self.crawl_manager = crawl_manager

    def render_GET(self, request):
        return json.dumps(self.crawl_manager.spider_list())


class CrawlService(Service):
    def __init__(self, cluster_info, crawl_manager):
        Service.__init__(self, cluster_info)
        self.crawl_manager = crawl_manager

    def render_GET(self, request):
        spider_name = request.args['spider'][0]
        self.crawl_manager.start_crawl(spider_name)
        data = dict()
        data['spider_name'] = spider_name
        data['start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps(data)


class CrawlStatusService(Service):
    def __init__(self, cluster_info, crawl_manager):
        Service.__init__(self, cluster_info)
        self.crawl_manager = crawl_manager

    def render_GET(self, request):
        return json.dumps(self.crawl_manager.crawler.stats.get_stats(), cls=JSON)




