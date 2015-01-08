# encoding=utf8
__author__ = 'wcong'
'''
control crawl and get crawl status
'''

from twisted.web import server, resource
from twisted.internet import reactor
from scrapy import management, log
import datetime
import json


class WebServiceManagement(management.Management):
    def __init__(self, port, cluster_info):
        self.port = port
        self.cluster_info = cluster_info
        self.start_time = datetime.datetime.now()
        self.__init_service()

    def __init_service(self):
        resource = Service(self.cluster_info)
        resource.putChild('node', NodeService(self.cluster_info))
        self.service = server.Site(resource)

    def start(self):
        reactor.listenTCP(self.port, self.service)

    def stop(self):
        now = datetime.datetime.now()
        log.msg(
            "start in :" + self.start_time.strftime("%Y-%m-%d %H:%I:%S") + ';end:' + now.strftime("%Y-%m-%d %H:%I:%S"))


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
        data['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")
        data['greeting'] = 'do not panic'
        data['message'] = 'for crawl'
        return json.dumps(data)


class NodeService(Service):
    def render_GET(self, request):
        return json.dumps(self.cluster_info, default=lambda o: o.__dict__)


class CrawlService(Service):
    def render_GET(self, request):
        log.msg("nothing?")





