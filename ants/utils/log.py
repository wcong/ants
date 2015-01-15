__author__ = 'wcong'
import logging
from twisted.python import failure
import traceback

ERROR = logging.ERROR
INFO = logging.INFO
WARNING = logging.WARNING
DEBUG = logging.DEBUG


def spider_log(message, *args, **kwargs):
    msg = ''
    if 'spider' in kwargs:
        msg += kwargs['spider'].name + ':'
    message_type = type(message)
    if message_type == str:
        msg += message
    elif message_type == failure.Failure:
        msg += traceback.format_tb(message.tb)
    else:
        msg += str(message)
    if 'level' in kwargs:
        logging.log(kwargs['level'], msg)
    logging.info(msg)