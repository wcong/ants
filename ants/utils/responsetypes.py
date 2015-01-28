"""
This module implements a class which returns the appropriate Response class
based on different criteria.

"""

from mimetypes import MimeTypes
from pkgutil import get_data
from cStringIO import StringIO

from ants.http import Response
from ants.utils.misc import load_object
from ants.utils.python import isbinarytext

class ResponseTypes(object):

    CLASSES = {
        'text/html': 'ants.http.HtmlResponse',
        'application/atom+xml': 'ants.http.XmlResponse',
        'application/rdf+xml': 'ants.http.XmlResponse',
        'application/rss+xml': 'ants.http.XmlResponse',
        'application/xhtml+xml': 'ants.http.HtmlResponse',
        'application/vnd.wap.xhtml+xml': 'ants.http.HtmlResponse',
        'application/xml': 'ants.http.XmlResponse',
        'application/json': 'ants.http.TextResponse',
        'application/javascript': 'ants.http.TextResponse',
        'application/x-javascript': 'ants.http.TextResponse',
        'text/xml': 'ants.http.XmlResponse',
        'text/*': 'ants.http.TextResponse',
    }

    def __init__(self):
        self.classes = {}
        self.mimetypes = MimeTypes()
        mimedata = get_data('ants', 'mime.types')
        self.mimetypes.readfp(StringIO(mimedata))
        for mimetype, cls in self.CLASSES.iteritems():
            self.classes[mimetype] = load_object(cls)

    def from_mimetype(self, mimetype):
        """Return the most appropriate Response class for the given mimetype"""
        if mimetype is None:
            return Response
        elif mimetype in self.classes:
            return self.classes[mimetype]
        else:
            basetype = "%s/*" % mimetype.split('/')[0]
            return self.classes.get(basetype, Response)

    def from_content_type(self, content_type, content_encoding=None):
        """Return the most appropriate Response class from an HTTP Content-Type
        header """
        if content_encoding:
            return Response
        mimetype = content_type.split(';')[0].strip().lower()
        return self.from_mimetype(mimetype)

    def from_content_disposition(self, content_disposition):
        try:
            filename = content_disposition.split(';')[1].split('=')[1]
            filename = filename.strip('"\'')
            return self.from_filename(filename)
        except IndexError:
            return Response

    def from_headers(self, headers):
        """Return the most appropriate Response class by looking at the HTTP
        headers"""
        cls = Response
        if 'Content-Type' in headers:
            cls = self.from_content_type(headers['Content-type'], \
                headers.get('Content-Encoding'))
        if cls is Response and 'Content-Disposition' in headers:
            cls = self.from_content_disposition(headers['Content-Disposition'])
        return cls

    def from_filename(self, filename):
        """Return the most appropriate Response class from a file name"""
        mimetype, encoding = self.mimetypes.guess_type(filename)
        if mimetype and not encoding:
            return self.from_mimetype(mimetype)
        else:
            return Response

    def from_body(self, body):
        """Try to guess the appropriate response based on the body content.
        This method is a bit magic and could be improved in the future, but
        it's not meant to be used except for special cases where response types
        cannot be guess using more straightforward methods."""
        chunk = body[:5000]
        if isbinarytext(chunk):
            return self.from_mimetype('application/octet-stream')
        elif "<html>" in chunk.lower():
            return self.from_mimetype('text/html')
        elif "<?xml" in chunk.lower():
            return self.from_mimetype('text/xml')
        else:
            return self.from_mimetype('text')

    def from_args(self, headers=None, url=None, filename=None, body=None):
        """Guess the most appropriate Response class based on the given arguments"""
        cls = Response
        if headers is not None:
            cls = self.from_headers(headers)
        if cls is Response and url is not None:
            cls = self.from_filename(url)
        if cls is Response and filename is not None:
            cls = self.from_filename(filename)
        if cls is Response and body is not None:
            cls = self.from_body(body)
        return cls

responsetypes = ResponseTypes()
