__author__ = 'wcong'
import ants


class DbItem(ants.Item):
    query = ants.Field()
    callback = ants.Field()
    request = ants.Field()