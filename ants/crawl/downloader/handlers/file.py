from w3lib.url import file_uri_to_path

from ants.utils.responsetypes import responsetypes
from ants.utils.decorator import defers


class FileDownloadHandler(object):

    def __init__(self, settings):
        pass

    @defers
    def download_request(self, request, spider):
        filepath = file_uri_to_path(request.url)
        body = open(filepath, 'rb').read()
        respcls = responsetypes.from_args(filename=filepath, body=body)
        return respcls(url=request.url, body=body)
