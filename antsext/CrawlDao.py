# encoding=utf8
import mysql
import sys

__author__ = 'wcong'

reload(sys)
sys.setdefaultencoding("utf-8")

import datetime
import re

db_goods_unique_key = ['source_goods_id', 'source_id']


class CrawlDao:
    html_tag = re.compile(r'<[^>]+>', re.S)

    def __init__(self):
        # conf = mysql.get_dw_conf()
        conf = mysql.get_local_conf()
        self.db = mysql.PDBC(conf)
        # self.slave_db = mysql.PDBC(mysql.get_slave_conf())

    def get_attr_key_id(self, source_id, key, cate_id):
        sql = 'select id from dw_crawl_attr_key where source_id =' + str(
            source_id) + ' and name = "' + key + '" and cate_id = ' + str(cate_id)
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        else:
            db_dict = dict()
            db_dict['source_id'] = source_id
            db_dict['name'] = key
            db_dict['cate_id'] = cate_id
            return self.insert_temple('dw_crawl_attr_key', db_dict)

    def get_attr_value_id(self, source_id, key_id, value):
        sql = 'select id from dw_crawl_attr_value where source_id =' + str(source_id) + ' and attr_key_id = ' + str(
            key_id) + ' and name = "' + value + '"'
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        else:
            db_dict = dict()
            db_dict['source_id'] = source_id
            db_dict['name'] = value
            db_dict['attr_key_id'] = key_id
            return self.insert_temple('dw_crawl_attr_value', db_dict)

    def get_goods_id(self, source_id, goods_id):
        sql = 'select id from dw_crawl_goods where source_id = ' + str(source_id) + ' and source_goods_id = "' + str(
            goods_id) + '"'
        data = self.db.get_data(sql)
        if len(data) == 0:
            return False
        else:
            return data[0]['id']

    def get_brand_id(self, source_id, name):
        sql = 'select id from dw_crawl_brand where source_id =' + str(source_id) + ' and name = "' + name + '"'
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        else:
            db_dict = dict()
            db_dict['source_id'] = source_id
            db_dict['name'] = name
            return self.insert_temple('dw_crawl_brand', db_dict)

    def insert_temple(self, table, dic, replace=False):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dic['gmt_create'] = gmt
        dic['gmt_modified'] = gmt
        if replace:
            action = 'replace'
        else:
            action = 'insert'
        sql = action + ' into ' + table + '(' + ','.join(dic.keys()) + ') values'
        value_list = list()
        for key, value in dic.items():
            value = str(value).replace('"', '')
            value_list.append('"' + self.html_tag.sub('', str(value)) + '"')
        sql += '(' + ','.join(value_list) + ')'
        print sql
        return self.db.insert_data(sql)

    def insert_or_update_goods(self, dic):
        select_sql = 'select id from dw_crawl_goods where source_id = ' + str(
            dic['source_id']) + ' and source_goods_id = "' + dic['source_goods_id'] + '"'
        data = self.db.get_data(select_sql)
        if data:
            return data[0]['id']
        else:
            return self.insert_temple("dw_crawl_goods", dic)

    # 这儿其实只用插入，没有更新
    def insert_or_update_goods_attr(self, dic):
        condition_list = list()
        for key, value in dic.items():
            condition_list.append(key + " = " + str(value))
        sql = 'select id from dw_crawl_goods_attr where ' + ' and '.join(condition_list)
        data = self.db.get_data(sql)
        if len(data) > 0:
            return
        self.insert_temple("dw_crawl_goods_attr", dic)

    def insert_batch_temple(self, table, batch_list, is_replace=False):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in batch_list:
            i['gmt_create'] = gmt
            i['gmt_modified'] = gmt
        action = 'insert'
        if is_replace:
            action = 'replace'
        sql = action + ' into ' + table + '(' + ','.join(batch_list[0].keys()) + ') values'
        value_list = list()
        for i in batch_list:
            inner_value_list = list()
            for key, value in i.items():
                if isinstance(value, str) or isinstance(value, unicode):
                    inner_value_list.append('"' + value + '"')
                else:
                    inner_value_list.append(str(value))
            value_list.append('(' + ','.join(inner_value_list) + ')')
        sql += ','.join(value_list)
        self.db.exec_data(sql)

    def get_car_id(self, source_id, level, parent_id, name, remarks=None):
        sql = 'select id from dw_crawl_car where source_id = ' + str(source_id) + ' and level = ' + str(
            level) + ' and parent_id=' + str(parent_id) + ' and name="' + name + '"'
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        else:
            insert_dic = dict()
            insert_dic['level'] = str(level)
            insert_dic['parent_id'] = str(parent_id)
            insert_dic['name'] = name
            insert_dic['source_id'] = str(source_id)
            if remarks:
                insert_dic['remarks'] = remarks
            return self.insert_temple("dw_crawl_car", insert_dic)

    def get_car_type(self, source_id, car_dic):
        car_id_list = list()
        brand_id = self.get_car_id(source_id, 1, 0, car_dic['brand'])
        car_id_list.append(brand_id)
        series_id = self.get_car_id(source_id, 2, brand_id, car_dic['series'])
        car_id_list.append(series_id)
        level = 3
        parent_id = series_id
        key_list = ['power', 'year', 'style']
        for key in key_list:
            if not key in car_dic.keys():
                break
            car_id = self.get_car_id(source_id, level, parent_id, car_dic[key])
            car_id_list.append(car_id)
            parent_id = car_id
            level += 1
        return car_id_list


    def save_goods_price(self, source_id, goods_id, price):
        goods_price_dic = dict()
        goods_price_dic['source_id'] = source_id
        goods_price_dic['goods_id'] = goods_id
        goods_price_dic['price'] = price
        goods_price_dic['crawl_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        self.insert_temple("dw_crawl_goods_price", goods_price_dic, True)

    def get_all_special_sign(self):
        sql = 'select name from db_tqmall_attr_value where key_id = 525 '
        data = self.db.get_data(sql)
        special_list = list()
        for i in data:
            special_list.append(i['attr_value'])
        return special_list

    # 从self.db中获取类目信息：id, pid, name
    def get_cate_by_source_pid(self, source_id, pid_list):
        if not pid_list:
            return None
        tmp_set = set()
        for e in pid_list:
            tmp_set.add(str(e))
        sql = 'select id, source_cate_id, source_pid, level, pid, name from dw_crawl_cate where source_id = ' + str(
            source_id) \
              + ' and pid in (' + ','.join(tmp_set) + ')'
        data = self.db.get_data(sql)
        return data

    def get_cate_id_by_name(self, source_cate_id, source_id, name):
        sql = 'select id from dw_crawl_cate where source_id=' + str(source_id) + ' and source_cate_id=' + str(
            source_cate_id) + ' and name="' + name + '"'
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        insert_dict = dict()
        insert_dict['source_cate_id'] = source_cate_id
        insert_dict['source_id'] = str(source_id)
        insert_dict['name'] = name
        return self.insert_temple("dw_crawl_cate", insert_dict)

    # 从self.db中获取类目信息：id, pid, name
    def get_cate_by_source(self, source_id):
        sql = 'select id, source_cate_id, source_pid, level, pid, name, ' \
              'source_cate_link from dw_crawl_cate where source_id = %d' % source_id
        data = self.db.get_data(sql)
        return data

    def get_cate_by_cateids(self, source_id, cate_ids):
        ids = []
        for id in cate_ids:
            if isinstance(id, str) or isinstance(id, unicode):
                ids.append(id)
            else:
                ids.append(str(id))
        sql_select = 'select id, cate_id from dw_crawl_cate where source_id = ' + str(
            source_id) + ' and cate_id in (' + ','.join(ids) + ')'
        return self.db.get_data(sql_select)


    def get_source_id(self, name):
        select_sql = 'select id from dw_crawl_source where name = "' + name + '"'
        data = self.db.get_data(select_sql)
        if data:
            return data[0]['id']
        else:
            db_dict = dict()
            db_dict['name'] = name
            return self.insert_temple('dw_crawl_source', db_dict)

    def get_store_id(self, db_dict):
        select_sql = 'select id from dw_crawl_store where source_id = ' + str(db_dict['source_id']) + \
                     ' and name = "' + db_dict['name'] + '"'
        data = self.db.get_data(select_sql)
        if data:
            return data[0]['id']
        else:
            return self.insert_temple('dw_crawl_store', db_dict)

    def insert_goods_store(self, source_id, goods_id, store_id):
        # goods_id已经区分了source_id，所以这儿我们就没有必要再查询source_id
        select_sql = 'select id from dw_crawl_goods_store where goods_id = ' + str(goods_id)
        data = self.db.get_data(select_sql)
        if data:
            return data[0]['id']
        else:
            db_dict = dict()
            db_dict['source_id'] = source_id
            db_dict['goods_id'] = goods_id
            db_dict['store_id'] = store_id
            return self.insert_temple('dw_crawl_goods_store', db_dict)

    # 插入数据，如果存在唯一索引执行更新操作，这儿通过on duplicate key update实现，所以主键不会执行更新操作
    def insert_or_update_template(self, table, db_dict, unique_key, primary_name='id'):
        select_sql = str()
        for key in unique_key:
            select_sql += key + ' = "' + str(db_dict[key]) + '" and '
        primary_key_id = 0
        if select_sql:
            select_sql = 'select id from %s where %s' % (table, select_sql[:-5])
            data = self.db.get_data(select_sql)
            if data:
                primary_key_id = data[0][primary_name]
        if primary_key_id > 0:
            gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_dict['gmt_modified'] = gmt
            value_list = list()
            for key, value in db_dict.items():
                value_list.append('%s = "%s"' % (key, str(value)))
            self.db.exec_data('update %s set %s %s' % (
                table, ','.join(value_list), ' where %s = %d' % (primary_name, primary_key_id)))
        else:
            primary_key_id = self.insert_temple(table, db_dict)
        return primary_key_id

    def insert_car_goods(self, source_id, car_id, goods_id):
        sql = 'select id from dw_crawl_car_goods where source_id = ' + str(source_id) \
              + ' and car_id = ' + str(car_id) + ' and goods_id = ' + str(goods_id)
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        else:
            db_dict = dict()
            db_dict['source_id'] = source_id
            db_dict['goods_id'] = goods_id
            db_dict['car_id'] = car_id
            return self.insert_temple('dw_crawl_car_goods', db_dict)

    def get_car_service_id(self, source_id, source_service_id, cate, name, suggest):
        sql = 'select id from dw_crawl_car_service where source_id=' + str(
            source_id) + ' and cate="' + cate + '" and name ="' + name + '"'
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        db_dict = dict()
        db_dict['source_id'] = str(source_id)
        db_dict['cate'] = cate
        db_dict['name'] = name
        db_dict['suggest'] = suggest
        if source_service_id:
            db_dict['source_service_id'] = source_service_id
        return self.insert_temple('dw_crawl_car_service', db_dict)

    def get_car_run_service_id(self, source_id, car_id, firsttime, mile, service_id, service_type,
                               service_suggest=None):
        sql = 'select id from  dw_crawl_car_run_service where source_id=' + str(source_id) + ' and car_id=' + str(
            car_id) + ' and firsttime="' + firsttime + '" and mile=' + str(mile) + " and service_id=" + str(service_id)
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        db_dict = dict()
        db_dict['source_id'] = str(source_id)
        db_dict['car_id'] = str(car_id)
        db_dict['firsttime'] = firsttime
        db_dict['mile'] = str(mile)
        db_dict['service_id'] = str(service_id)
        db_dict['service_type'] = str(service_type)
        if service_suggest:
            db_dict['service_suggest'] = service_suggest
        return self.insert_temple('dw_crawl_car_run_service', db_dict)

    def add_car_run_service_goods(self, source_id, car_run_service_id, source_goods_id, goods_id=None):
        sql = 'select id from dw_crawl_car_run_service_goods where source_id=' + str(
            source_id) + ' and car_run_service_id=' + str(
            car_run_service_id) + ' and source_goods_id="' + source_goods_id + '"'
        data = self.db.get_data(sql)
        if data:
            return data[0]['id']
        db_dict = dict()
        db_dict['source_id'] = str(source_id)
        db_dict['car_run_service_id'] = str(car_run_service_id)
        db_dict['source_goods_id'] = source_goods_id
        if goods_id:
            db_dict['goods_id'] = str(goods_id)
        return self.insert_temple('dw_crawl_car_run_service_goods', db_dict)