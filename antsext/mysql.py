# -*- coding: UTF-8 -*-

__author__ = 'wcong'

import MySQLdb
import MySQLdb.cursors


def create_conf():
    conf = dict()
    conf['host'] = '114.215.237.91'
    conf['user'] = 'otter_all'
    conf['passwd'] = 'tqmall2014'
    conf['db'] = 'tqdw'
    conf['port'] = 3306
    conf['charset'] = 'utf8'
    return conf


def get_dw_conf():
    conf = create_conf()
    conf['host'] = '121.199.42.91'
    conf['user'] = 'crawl_all'
    conf['passwd'] = 'crawl.tqmall2014'
    conf['db'] = 'crawl'
    return conf


def get_slave_conf():
    conf = create_conf()
    conf['host'] = '121.199.23.203'
    conf['user'] = 'shop_r_wcong'
    conf['passwd'] = 'Ki8Hd9Mckd73Jdiw'
    conf['db'] = 'ol_autoparts'
    return conf

def get_local_conf():
    conf = create_conf()
    conf['host'] = '127.0.0.1'
    conf['user'] = 'root'
    conf['passwd'] = ''
    conf['db'] = 'crawl'
    return conf

def get_test_conf():
    conf = create_conf()
    conf['host'] = '112.124.61.169'
    conf['user'] = 'test_autoparts'
    conf['passwd'] = 'UmbAjWwUY2GLJxGy'
    conf['db'] = 'test_autoparts'
    return conf


def get_stable_conf():
    conf = create_conf()
    conf['host'] = '121.199.42.91'
    conf['user'] = 'shop_crud_stat'
    conf['passwd'] = 'NDInduwns82bd9BED2'
    conf['db'] = 'stable_autoparts'
    return conf


class PDBC:
    def __init__(self, conf):
        self.conn = MySQLdb.connect(host=conf['host'], user=conf['user'], passwd=conf['passwd'], db=conf['db'],
                                    port=conf['port'], charset=conf['charset'], cursorclass=MySQLdb.cursors.DictCursor)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def get_data(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def get_cursor(self, sql):
        self.cur.execute(sql)
        return self.cur

    def exec_data(self, sql):
        result = self.cur.execute(sql)
        self.conn.commit()
        return result

    # 插入函数，返回最后插入的主键id
    def insert_data(self, sql):
        self.cur.execute(sql)
        new_id = int(self.cur.lastrowid)
        self.conn.commit()
        return new_id