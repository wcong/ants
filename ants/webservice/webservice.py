# encoding=utf8
__author__ = 'wcong'
'''
control crawl and get crawl status
'''

from twisted.web import server, resource
from twisted.internet import reactor
from ants import manager, log
from ants.utils.jsonextends import JSON
import datetime
import json


class WebServiceManager(manager.Manager):
    def __init__(self, setting, node_manager):
        self.setting = setting
        self.port = self.setting.get('HTTP_PORT')
        self.node_manager = node_manager
        self.start_time = datetime.datetime.now()
        self.__init_service()

    def __init_service(self):
        resource = Service(self.node_manager)
        resource.putChild('node', NodeService(self.node_manager))
        resource.putChild('spider_list', SpiderListService(self.node_manager))
        resource.putChild('crawl', CrawlService(self.node_manager))
        resource.putChild('crawl_status', CrawlStatusService(self.node_manager))
        self.service = server.Site(resource)

    def start(self):
        reactor.listenTCP(self.port, self.service)

    def stop(self):
        now = datetime.datetime.now()
        log.msg(
            "webservice start in :" + self.start_time.strftime("%Y-%m-%d %H:%M:%S") + ';end:' + now.strftime(
                "%Y-%m-%d %H:%M:%S"))


class Service(resource.Resource):
    def __init__(self, node_manager):
        resource.Resource.__init__(self)
        self.cluster_info = node_manager

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
        return json.dumps(self.node_manager.cluster_manager.cluster_info, cls=JSON)


class SpiderListService(Service):

    def render_GET(self, request):
        return json.dumps(self.node_manager.crawl_manager.spider_list())


class CrawlService(Service):
    '''
    send to node that we should start a crawl job
    '''

    def render_GET(self, request):
        spider_name = request.args['spider'][0]
        self.node_manager.start_a_crawl(spider_name)
        data = dict()
        data['spider_name'] = spider_name
        data['start_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return json.dumps(data)


class CrawlStatusService(Service):
    def render_GET(self, request):
        return json.dumps(self.node_manager.crawl_manager.crawler.stats.get_stats(), cls=JSON)




