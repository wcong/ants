from collections import deque

from twisted.python.failure import Failure
from twisted.internet import defer

from ants.utils.defer import defer_result, defer_succeed, parallel, iter_errback
from ants.utils.spider import iterate_spider_output
from ants.utils.misc import load_object
from ants.exceptions import CloseSpider, DropItem, IgnoreRequest
from ants import signals
from ants.http import Request, Response
from ants.item import BaseItem
from ants.crawl.spidermiddleware import SpiderMiddlewareManager
from ants.utils import log


class Slot(object):
    """Scraper slot (one per running spider)"""

    MIN_RESPONSE_SIZE = 1024

    def __init__(self, max_active_size=5000000):
        self.max_active_size = max_active_size
        self.queue = deque()
        self.active = set()
        self.active_size = 0
        self.itemproc_size = 0
        self.closing = None

    def add_response_request(self, response, request):
        deferred = defer.Deferred()
        self.queue.append((response, request, deferred))
        if isinstance(response, Response):
            self.active_size += max(len(response.body), self.MIN_RESPONSE_SIZE)
        else:
            self.active_size += self.MIN_RESPONSE_SIZE
        return deferred

    def next_response_request_deferred(self):
        response, request, deferred = self.queue.popleft()
        self.active.add(request)
        return response, request, deferred

    def finish_response(self, response, request):
        self.active.remove(request)
        if isinstance(response, Response):
            self.active_size -= max(len(response.body), self.MIN_RESPONSE_SIZE)
        else:
            self.active_size -= self.MIN_RESPONSE_SIZE

    def is_idle(self):
        return not (self.queue or self.active)

    def needs_backout(self):
        return self.active_size > self.max_active_size


class Scraper(object):
    def __init__(self, engine, spider):
        self.slot = None
        self.spidermw = SpiderMiddlewareManager.from_crawler(engine)

        itemproc_cls = load_object(engine.settings['ITEM_PROCESSOR'])
        self.itemproc = itemproc_cls.from_crawler(engine)

        self.concurrent_items = engine.settings.getint('CONCURRENT_ITEMS')

        self.engine = engine
        self.signals = engine.signals

        self.slot = Slot()
        self.itemproc.open_spider(spider)

    def close_spider(self, spider):
        """Close a spider being scraped and release its resources"""
        slot = self.slot
        slot.closing = defer.Deferred()
        slot.closing.addCallback(self.itemproc.close_spider)
        self._check_if_closing(spider, slot)
        return slot.closing

    def is_idle(self):
        """Return True if there isn't any more spiders to process"""
        return not self.slot

    @staticmethod
    def _check_if_closing(spider, slot):
        if slot.closing and slot.is_idle():
            slot.closing.callback(spider)

    def enqueue_scrape(self, response, request, spider):
        slot = self.slot
        dfd = slot.add_response_request(response, request)

        def finish_scraping(_):
            slot.finish_response(response, request)
            self._check_if_closing(spider, slot)
            self._scrape_next(spider, slot)
            return _

        dfd.addBoth(finish_scraping)
        dfd.addErrback(log.spider_log, 'Scraper bug processing %s' % request, spider=spider)
        self._scrape_next(spider, slot)
        return dfd

    def _scrape_next(self, spider, slot):
        while slot.queue:
            response, request, deferred = slot.next_response_request_deferred()
            self._scrape(response, request, spider).chainDeferred(deferred)

    def _scrape(self, response, request, spider):
        """Handle the downloaded response or failure trough the spider
        callback/errback"""
        assert isinstance(response, (Response, Failure))

        dfd = self._scrape2(response, request, spider)  # returns spiders processed output
        dfd.addErrback(self.handle_spider_error, request, response, spider)
        dfd.addCallback(self.handle_spider_output, request, response, spider)
        return dfd

    def _scrape2(self, request_result, request, spider):
        """Handle the different cases of request's result been a Response or a
        Failure"""
        if not isinstance(request_result, Failure):
            return self.spidermw.scrape_response(self.call_spider, request_result, request, spider)
        else:
            # FIXME: don't ignore errors in spider middleware
            dfd = self.call_spider(request_result, request, spider)
            return dfd.addErrback(self._log_download_errors, request_result, request, spider)

    @staticmethod
    def call_spider(result, request, spider):
        result.request = request
        dfd = defer_result(result)
        dfd.addCallbacks(request.callback or spider.parse, request.errback)
        return dfd.addCallback(iterate_spider_output)

    def handle_spider_error(self, _failure, request, response, spider):
        exc = _failure.value
        if isinstance(exc, CloseSpider):
            self.engine.engine.close_spider(spider, exc.reason or 'cancelled')
            return
        log.spider_log(_failure, "Spider error processing %s" % request, spider=spider)
        self.signals.send_catch_log(signal=signals.spider_error, failure=_failure, response=response, pider=spider)
        self.engine.stats.inc_value("spider_exceptions/%s" % _failure.value.__class__.__name__, spider=spider)
        self.engine.send_request_result(request, str(exc))

    def handle_spider_output(self, result, request, response, spider):
        if not result:
            return defer_succeed(None)
        it = iter_errback(result, self.handle_spider_error, request, response, spider)
        dfd = parallel(it, self.concurrent_items,
                       self._process_spidermw_output, request, response, spider)
        return dfd

    def _process_spidermw_output(self, output, request, response, spider):
        """Process each Request/Item (given in the output parameter) returned
        from the given spider
        """
        if isinstance(output, Request):
            self.engine.add_request(request, output)
        elif isinstance(output, BaseItem):
            self.slot.itemproc_size += 1
            dfd = self.itemproc.process_item(output, spider)
            dfd.addBoth(self._itemproc_finished, output, request, response, spider)
            return dfd
        elif output is None:
            self.engine.send_request_result()
        else:
            typename = type(output).__name__
            msg = 'Spider must return Request, BaseItem or None, got ' + typename + ' in ' + request.url
            log.spider_log(msg, level=log.ERROR, spider=spider)
            self.engine.send_request_result(request, msg)

    @staticmethod
    def _log_download_errors(spider_failure, download_failure, request, spider):
        """Log and silence errors that come from the engine (typically download
        errors that got propagated thru here)
        """
        if isinstance(download_failure, Failure) \
                and not download_failure.check(IgnoreRequest):
            if download_failure.frames:
                log.spider_log('Error downloading %s' % request, spider=spider, level=log.ERROR)
            else:
                errmsg = download_failure.getErrorMessage()
                if errmsg:
                    log.spider_log('Error downloading ' + request.url + ':' + errmsg,
                                   level=log.ERROR, spider=spider)

        if spider_failure is not download_failure:
            return spider_failure

    def _itemproc_finished(self, output, item, request, response, spider):
        """ItemProcessor finished for the given ``item`` and returned ``output``
        """
        self.slot.itemproc_size -= 1
        if isinstance(output, Failure):
            ex = output.value
            if isinstance(ex, DropItem):
                log.spider_log('scrape error:' + ex.message + ':in:' + response.url, spider=spider, level=log.ERROR)
                return self.signals.send_catch_log_deferred(signal=signals.item_dropped,
                                                            item=item,
                                                            response=response,
                                                            spider=spider,
                                                            exception=output.value)
            else:
                log.spider_log('Error processing %s' % item, spider=spider, level=log.ERROR)
            self.engine.send_request_result(request, ex)
        else:
            log.spider_log('scrape ok in:' + response.url, spider=spider)
            self.engine.send_request_result(request)
            return self.signals.send_catch_log_deferred(signal=signals.item_scraped,
                                                        item=output,
                                                        response=response,
                                                        spider=spider)