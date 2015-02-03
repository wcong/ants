#!/usr/bin/env python
# encoding=utf8
import os
from ants.bootstrap.bootstrap import Bootstrap
import sys
import logging

logging.basicConfig(format="[%(asctime)s %(module)s %(lineno)d]%(levelname)s:%(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename="logs/crawl.log",
                    level=logging.DEBUG)

pwd = os.getcwd()
if 'PYTHONPATH' in os.environ:
    python_path = os.environ['PYTHONPATH']
    if python_path.find(pwd) == -1:
        os.environ['PYTHONPATH'] = python_path + ';' + pwd
else:
    os.environ['PYTHONPATH'] = pwd

if __name__ == '__main__':
    Bootstrap(sys.argv[1:]).start()
