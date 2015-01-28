"""Download handlers for different schemes"""

from ants.utils.exceptions import NotSupported, NotConfigured
from ants.utils.httpobj import urlparse_cached
from ants.utils.misc import load_object


class DownloadHandlers(object):
    def __init__(self, engine):
        self._handlers = {}
        self._notconfigured = {}
        handlers = engine.settings.get('DOWNLOAD_HANDLERS_BASE')
        handlers.update(engine.settings.get('DOWNLOAD_HANDLERS', {}))
        for scheme, clspath in handlers.iteritems():
            # Allow to disable a handler just like any other
            # component (extension, middleware, etc).
            if clspath is None:
                continue
            cls = load_object(clspath)
            try:
                dh = cls(engine.settings)
            except NotConfigured as ex:
                self._notconfigured[scheme] = str(ex)
            else:
                self._handlers[scheme] = dh


    def download_request(self, request, spider):
        scheme = urlparse_cached(request).scheme
        try:
            handler = self._handlers[scheme].download_request
        except KeyError:
            msg = self._notconfigured.get(scheme, \
                                          'no handler available for that scheme')
            raise NotSupported("Unsupported URL scheme '%s': %s" % (scheme, msg))
        return handler(request, spider)

