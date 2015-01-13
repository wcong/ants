"""Download handlers for different schemes"""

from twisted.internet import defer
from ants.exceptions import NotSupported, NotConfigured
from ants.utils.httpobj import urlparse_cached
from ants.utils.misc import load_object
from ants import signals


class DownloadHandlers(object):

    def __init__(self, crawler):
        self._handlers = {}
        self._notconfigured = {}
        handlers = crawler.settings.get('DOWNLOAD_HANDLERS_BASE')
        handlers.update(crawler.settings.get('DOWNLOAD_HANDLERS', {}))
        for scheme, clspath in handlers.iteritems():
            # Allow to disable a handler just like any other
            # component (extension, middleware, etc).
            if clspath is None:
                continue
            cls = load_object(clspath)
            try:
                dh = cls(crawler.settings)
            except NotConfigured as ex:
                self._notconfigured[scheme] = str(ex)
            else:
                self._handlers[scheme] = dh

        crawler.signals.connect(self._close, signals.engine_stopped)

    def download_request(self, request, spider):
        scheme = urlparse_cached(request).scheme
        try:
            handler = self._handlers[scheme].download_request
        except KeyError:
            msg = self._notconfigured.get(scheme, \
                    'no handler available for that scheme')
            raise NotSupported("Unsupported URL scheme '%s': %s" % (scheme, msg))
        return handler(request, spider)

    @defer.inlineCallbacks
    def _close(self, *_a, **_kw):
        for dh in self._handlers.values():
            if hasattr(dh, 'close'):
                yield dh.close()
