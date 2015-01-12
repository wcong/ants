__author__ = 'wcong'

import unittest
import datetime
import json
from ants.utils.jsonextends import JSON


class JSONExtendsTest(unittest.TestCase):
    def test(self):
        data = dict()
        data['1'] = 1
        data['now'] = datetime.datetime.now()
        print json.dumps(data,de)


if __name__ == '__main__':
    unittest.main()