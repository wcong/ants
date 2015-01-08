__author__ = 'wcong'

import json
import datetime


class JSON(json.JSONEncoder):
    def default(self, o):
        o_type = type(o)
        if o_type == datetime.datetime:
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif o_type == datetime.date:
            return o.strftime('%Y-%m-%d')
        elif hasattr(o, '__dict__'):
            return o.__dict__
        else:
            return o