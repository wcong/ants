__author__ = 'wcong'
import logging


def spider_log(*args, **kwargs):
    msg = ''
    if 'spider' in kwargs:
        msg += kwargs['spider'].name + ':'
    logging.info()