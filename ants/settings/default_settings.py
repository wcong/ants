"""
This module contains the default values for all settings used by Scrapy.

For more information about these settings you can read the settings
documentation in docs/topics/settings.rst

Scrapy developers, if you add a setting here remember to:

* add it in alphabetical order
* group similar settings without leaving blank lines
* add its documentation to the available settings documentation
  (docs/topics/settings.rst)

"""

import os
import sys
from importlib import import_module
from os.path import join, abspath, dirname

AJAXCRAWL_ENABLED = False

BOT_NAME = 'scrapybot'

CLOSESPIDER_TIMEOUT = 0
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
CLOSESPIDER_ERRORCOUNT = 0

COMMANDS_MODULE = ''

COMPRESSION_ENABLED = True

CONCURRENT_ITEMS = 100

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 0

COOKIES_ENABLED = True
COOKIES_DEBUG = False

DEFAULT_ITEM_CLASS = 'ants.item.Item'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
}

DEPTH_LIMIT = 0
DEPTH_STATS = True
DEPTH_PRIORITY = 0

DNSCACHE_ENABLED = True

DOWNLOAD_DELAY = 0

DOWNLOAD_HANDLERS = {}
DOWNLOAD_HANDLERS_BASE = {
    'file': 'ants.core.downloader.handlers.file.FileDownloadHandler',
    'http': 'ants.core.downloader.handlers.http.HTTPDownloadHandler',
    'https': 'ants.core.downloader.handlers.http.HTTPDownloadHandler',
    's3': 'ants.core.downloader.handlers.s3.S3DownloadHandler',
    'ftp': 'ants.core.downloader.handlers.ftp.FTPDownloadHandler',
}

DOWNLOAD_TIMEOUT = 180  # 3mins

DOWNLOADER = 'ants.core.downloader.Downloader'

DOWNLOADER_HTTPCLIENTFACTORY = 'ants.core.downloader.webclient.ScrapyHTTPClientFactory'
DOWNLOADER_CLIENTCONTEXTFACTORY = 'ants.core.downloader.contextfactory.ScrapyClientContextFactory'

DOWNLOADER_MIDDLEWARES = {}

DOWNLOADER_MIDDLEWARES_BASE = {
    # Engine side
    'ants.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': 100,
    'ants.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': 300,
    'ants.contrib.downloadermiddleware.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'ants.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 400,
    'ants.contrib.downloadermiddleware.retry.RetryMiddleware': 500,
    'ants.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': 550,
    'ants.contrib.downloadermiddleware.ajaxcrawl.AjaxCrawlMiddleware': 560,
    'ants.contrib.downloadermiddleware.redirect.MetaRefreshMiddleware': 580,
    'ants.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware': 590,
    'ants.contrib.downloadermiddleware.redirect.RedirectMiddleware': 600,
    'ants.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
    'ants.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 750,
    'ants.contrib.downloadermiddleware.chunked.ChunkedTransferMiddleware': 830,
    'ants.contrib.downloadermiddleware.stats.DownloaderStats': 850,
    'ants.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': 900,
    # Downloader side
}

DOWNLOADER_STATS = True

DUPEFILTER_CLASS = 'ants.dupefilter.RFPDupeFilter'

try:
    EDITOR = os.environ['EDITOR']
except KeyError:
    if sys.platform == 'win32':
        EDITOR = '%s -m idlelib.idle'
    else:
        EDITOR = 'vi'

EXTENSIONS = {}

EXTENSIONS_BASE = {
    'ants.contrib.corestats.CoreStats': 0,
    # 'ants.webservice.WebService': 0,
    'ants.telnet.TelnetConsole': 0,
    'ants.contrib.memusage.MemoryUsage': 0,
    'ants.contrib.memdebug.MemoryDebugger': 0,
    'ants.contrib.closespider.CloseSpider': 0,
    'ants.contrib.feedexport.FeedExporter': 0,
    'ants.contrib.logstats.LogStats': 0,
    'ants.contrib.spiderstate.SpiderState': 0,
    'ants.contrib.throttle.AutoThrottle': 0,
}

FEED_URI = None
FEED_URI_PARAMS = None  # a function to extend uri arguments
FEED_FORMAT = 'jsonlines'
FEED_STORE_EMPTY = False
FEED_STORAGES = {}
FEED_STORAGES_BASE = {
    '': 'ants.contrib.feedexport.FileFeedStorage',
    'file': 'ants.contrib.feedexport.FileFeedStorage',
    'stdout': 'ants.contrib.feedexport.StdoutFeedStorage',
    's3': 'ants.contrib.feedexport.S3FeedStorage',
    'ftp': 'ants.contrib.feedexport.FTPFeedStorage',
}
FEED_EXPORTERS = {}
FEED_EXPORTERS_BASE = {
    'json': 'ants.contrib.exporter.JsonItemExporter',
    'jsonlines': 'ants.contrib.exporter.JsonLinesItemExporter',
    'jl': 'ants.contrib.exporter.JsonLinesItemExporter',
    'csv': 'ants.contrib.exporter.CsvItemExporter',
    'xml': 'ants.contrib.exporter.XmlItemExporter',
    'marshal': 'ants.contrib.exporter.MarshalItemExporter',
    'pickle': 'ants.contrib.exporter.PickleItemExporter',
}

HTTPCACHE_ENABLED = False
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_MISSING = False
HTTPCACHE_STORAGE = 'ants.contrib.httpcache.FilesystemCacheStorage'
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_IGNORE_SCHEMES = ['file']
HTTPCACHE_DBM_MODULE = 'anydbm'
HTTPCACHE_POLICY = 'ants.contrib.httpcache.DummyPolicy'

ITEM_PROCESSOR = 'ants.contrib.pipeline.ItemPipelineManager'

ITEM_PIPELINES = {}
ITEM_PIPELINES_BASE = {}

LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FORMATTER = 'ants.logformatter.LogFormatter'
LOG_STDOUT = False
LOG_LEVEL = 'DEBUG'
LOG_FILE = None

LOG_UNSERIALIZABLE_REQUESTS = False

LOGSTATS_INTERVAL = 60.0

MAIL_HOST = 'localhost'
MAIL_PORT = 25
MAIL_FROM = 'ants@localhost'
MAIL_PASS = None
MAIL_USER = None

MEMDEBUG_ENABLED = False  # enable memory debugging
MEMDEBUG_NOTIFY = []  # send memory debugging report by mail at engine shutdown

MEMUSAGE_ENABLED = False
MEMUSAGE_LIMIT_MB = 0
MEMUSAGE_NOTIFY_MAIL = []
MEMUSAGE_REPORT = False
MEMUSAGE_WARNING_MB = 0

METAREFRESH_ENABLED = True
METAREFRESH_MAXDELAY = 100

NEWSPIDER_MODULE = ''

RANDOMIZE_DOWNLOAD_DELAY = True

REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20  # uses Firefox default setting
REDIRECT_PRIORITY_ADJUST = +2

REFERER_ENABLED = True

RETRY_ENABLED = True
RETRY_TIMES = 2  # initial response + 2 retries = 3 requests
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408]
RETRY_PRIORITY_ADJUST = -1

ROBOTSTXT_OBEY = False

SCHEDULER = 'ants.core.scheduler.Scheduler'
SCHEDULER_DISK_QUEUE = 'ants.squeue.PickleLifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'ants.squeue.LifoMemoryQueue'

SPIDER_MANAGER_CLASS = 'ants.spidermanager.SpiderManager'

SPIDER_MIDDLEWARES = {}

SPIDER_MIDDLEWARES_BASE = {
    # Engine side
    'ants.contrib.spidermiddleware.httperror.HttpErrorMiddleware': 50,
    'ants.contrib.spidermiddleware.offsite.OffsiteMiddleware': 500,
    'ants.contrib.spidermiddleware.referer.RefererMiddleware': 700,
    'ants.contrib.spidermiddleware.urllength.UrlLengthMiddleware': 800,
    'ants.contrib.spidermiddleware.depth.DepthMiddleware': 900,
    # Spider side
}

SPIDER_MODULES = ['spider']

STATS_CLASS = 'ants.statscol.MemoryStatsCollector'
STATS_DUMP = True

STATSMAILER_RCPTS = []

TEMPLATES_DIR = abspath(join(dirname(__file__), '..', 'templates'))

URLLENGTH_LIMIT = 2083

USER_AGENT = 'Scrapy/%s (+http://ants.org)' % import_module('ants').__version__

TELNETCONSOLE_ENABLED = 1
TELNETCONSOLE_PORT = [6023, 6073]
TELNETCONSOLE_HOST = '127.0.0.1'

WEBSERVICE_ENABLED = True
WEBSERVICE_LOGFILE = None
WEBSERVICE_PORT = [6080, 7030]
WEBSERVICE_HOST = '127.0.0.1'
WEBSERVICE_RESOURCES = {}
WEBSERVICE_RESOURCES_BASE = {
    'ants.contrib.webservice.crawler.CrawlerResource': 1,
    'ants.contrib.webservice.enginestatus.EngineStatusResource': 1,
    'ants.contrib.webservice.stats.StatsResource': 1,
}

SPIDER_CONTRACTS = {}
SPIDER_CONTRACTS_BASE = {
    'ants.contracts.default.UrlContract': 1,
    'ants.contracts.default.ReturnsContract': 2,
    'ants.contracts.default.ScrapesContract': 3,
}
'''
this is where cluster setting
'''

CLUSTER_NAME = 'ants'
TRANSPORT_PORT = 8300
HTTP_PORT = 8200
