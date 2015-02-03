#!/usr/bin/env python
# encoding=utf8
import os
from ants.bootstrap.bootstrap import Bootstrap
import sys

pwd = os.getcwd()
python_path = os.environ['PYTHONPATH']
if python_path.find(pwd) == -1:
    os.environ['PYTHONPATH'] = python_path + ';' + pwd

if __name__ == '__main__':
    Bootstrap(sys.argv[1:]).start()