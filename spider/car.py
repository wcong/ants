__author__ = 'wcong'

import ants
import time
from antsext import CrawlDao
import random
import re
import datetime


class CarSpider(ants.Spider):
    name = 'yang_che_car_spider'

    start_urls = [
        'http://www.yangche51.com/'
    ]
    source_id = '6'

    url = 'http://www.yangche51.com/handlers/choosecar/choosecarprovider.aspx'

    domain = 'http://www.yangche51.com'

    cookie_jar = 0

    debug = True

    def __init__(self, **kwargs):
        super(CarSpider, self).__init__(**kwargs)
        self.dao = CrawlDao.CrawlDao()
        self.pattern = re.compile(r'\d+')
        now = datetime.datetime.now()
        self.crawled_car_run = set()
        sql = 'select  car_id,firsttime,mile from dw_crawl_car_run_service group by car_id,firsttime,mile'
        data = self.dao.db.get_data(sql)
        for i in data:
            self.crawled_car_run.add(str(i['car_id']) + '_' + i['firsttime'] + '_' + str(i['mile']))
        self.year = now.year
        self.month = now.month


    def parse(self, response):
        param_list = [
            'json={"Alphabet":null,"AutoBrandId":0,"AutoModelId":0,"AutoModelSubId":0,"ChooseType":1,"MainAutoModelID":0,"SubIds":null,"Year":0}',
            '_:' + str(int(time.time()))
        ]
        yield ants.Request(self.url + '?' + '&'.join(param_list), callback='parse_words')

    def parse_words(self, response):
        words_div = response.xpath('//div[@class="brandChoose"]/ul/li')[1:]
        for word_div in words_div:
            json = word_div.xpath('./a/@choosecarparam').extract()[0]
            timestamp = str(int(time.time()))
            yield ants.Request(self.url + '?' + 'json=' + str(json) + '&_=' + timestamp, callback='parse_brand')
            if self.debug:
                break

    def parse_brand(self, response):
        brand_list = response.xpath('//div[@id="choosecar1_div_choosecar"]/div')[1].xpath('./ul/li/a')
        for brand in brand_list:
            title = brand.xpath('./@title').extract()[0]
            json = brand.xpath('./@choosecarparam').extract()[0]
            timestamp = str(int(time.time()))
            meta = dict(response.meta)
            car_id = self.dao.get_car_id(self.source_id, 1, 0, title)
            meta['brand_id'] = car_id
            yield ants.Request(self.url + '?' + 'json=' + str(json) + '&_=' + timestamp,
                               callback='parse_series',
                               meta=meta)
            if self.debug:
                break

    def parse_series(self, response):
        content_div = response.xpath('//div[@id="choosecar1_div_choosecar"]/div')[1]
        nature_list = content_div.xpath('./b')
        ul_list = content_div.xpath('./ul')
        meta = response.meta
        for i, ul in enumerate(ul_list):
            nature = nature_list[i].xpath('./text()').extract()[0].strip()
            series_list = ul.xpath('./li/a')
            for series in series_list:
                series_name = series.xpath('./@title').extract()[0].strip()
                json = series.xpath('./@choosecarparam').extract()[0].strip()
                timestamp = str(int(time.time()))
                car_name = nature + ':' + series_name
                car_id = self.dao.get_car_id(self.source_id, 2, meta['brand_id'], car_name)
                meta['series_id'] = car_id
                yield ants.Request(self.url + '?' + 'json=' + str(json) + '&_=' + timestamp,
                                   callback='parse_power',
                                   meta=meta)
                if self.debug:
                    break
            if self.debug:
                break

    def parse_power(self, response):
        content_div = response.xpath('//div[@id="choosecar1_div_choosecar"]/div')[1]
        power_list = content_div.xpath('./ul/li/a')
        meta = response.meta
        for power in power_list:
            power_name = power.xpath('./@title').extract()[0]
            json = power.xpath('./@choosecarparam').extract()[0]
            timestamp = str(int(time.time()))
            car_id = self.dao.get_car_id(self.source_id, 3, meta['series_id'], power_name)
            meta['power_id'] = car_id
            yield ants.Request(self.url + '?' + 'json=' + str(json) + '&_=' + timestamp,
                               callback='parse_year',
                               meta=meta)
            if self.debug:
                break

    def parse_year(self, response):
        content_div = response.xpath('//div[@id="choosecar1_div_choosecar"]/div')[1]
        year_list = content_div.xpath('./ul/li/a')
        meta = response.meta
        timestamp = str(int(time.time()))
        for i, year in enumerate(year_list):
            year_name = year.xpath('./@title').extract()[0]
            json_param = year.xpath('./@choosecarparam').extract()[0]
            car_id = self.dao.get_car_id(self.source_id, 4, meta['power_id'], year_name, json_param)
            param = 'json=' + json_param + '&_=' + timestamp
            meta['car_id'] = car_id
            meta['year'] = year_name
            first_time_list = self.make_mile_and_year_group(year_name)
            for j, first_time in enumerate(first_time_list):
                meta['mile'] = first_time[1]
                meta['firsttime'] = first_time[0]
                meta['cookiejar'] = self.cookie_jar
                key = str(car_id) + '_' + meta['firsttime'] + '_' + str(meta['mile'])
                if key in self.crawled_car_run:
                    continue
                self.cookie_jar += 1
                yield ants.Request(self.url + '?' + param + '&jar=' + str(meta['cookiejar']),
                                   meta=meta,
                                   callback='go_to_input_page')
            if self.debug and i > 1:
                break

    mile_list = range(1000, 150000, 1000)

    def make_mile_and_year_group(self, year):
        start_year = self.pattern.match(year)
        start_year = int(start_year.group())
        first_time_list = list()
        for range_year in range(start_year, self.year):
            for month in range(1, 13):
                month_str = str(month) if month > 10 else '0' + str(month)
                first_time_list.append(
                    (str(range_year) + month_str, ((self.year - range_year) * 12 - month + self.month ) * 1000))
        for month in range(1, self.month + 1):
            month_str = str(month) if month > 10 else '0' + str(month)
            first_time_list.append((str(self.year) + month_str, month * 1000))
        return first_time_list

    def go_to_input_page(self, response):
        yield ants.Request(self.domain + '/baoyang/?' + str(random.random()) + '#check',
                           callback='input_mile',
                           meta=response.meta)

    def input_mile(self, response):
        meta = response.meta
        next_request = ants.Request(
            self.domain + '/baoyang/step2.html?curmileage=' + str(
                meta['mile']) + '&firsttime=' + meta['firsttime'] + '&jar=' + str(
                meta['cookiejar']),
            self.parse_service, meta=meta)
        return next_request


    def parse_service(self, response):
        detail_list = response.xpath('//div[@class="tableSetp2"]/div[contains(@class,"delist")]')
        detail_list_list = [detail_list]
        table_step2_list = response.xpath('//div[@id="dd_tablestep2mt"]')
        detail_list_list.append(table_step2_list[1].xpath('./div[contains(@class,"delist")]'))
        detail_list_list.append(table_step2_list[3].xpath('./div[contains(@class,"delist")]'))
        service_value_list = list()
        p_name_service_id_map = dict()
        for type, detail_list in enumerate(detail_list_list, start=1):
            for detail in detail_list:
                one_service_value_list = list()
                service_value_list.append(one_service_value_list)
                title = detail.xpath('./dl/dt/b/text()').extract()[0].split('.')[1].strip()
                service_div_list = detail.xpath('./div/table/tbody/tr')
                for service_div in service_div_list:
                    td_list = service_div.xpath('./td')
                    source_service_id = td_list[0].xpath('./input')[0].xpath('./@value').extract()[0]
                    second_value = td_list[0].xpath('./input')[1].xpath('./@value').extract()[0]
                    p_name = source_service_id + '_' + second_value
                    one_service_value_list.append(p_name)
                    service_name = td_list[1].xpath('./text()').extract()[0].strip()
                    service_suggest = td_list[2].xpath('./span/text()').extract()
                    if service_suggest:
                        service_suggest = service_suggest[0].strip()
                        car_suggest = td_list[2].xpath('./text()').extract()[0].strip()
                    else:
                        service_suggest = td_list[2].xpath('./text()').extract()
                        if service_suggest:
                            service_suggest = service_suggest[0].strip()
                        else:
                            service_suggest = ''
                        car_suggest = None
                    service_id = self.dao.get_car_service_id(self.source_id,
                                                             source_service_id,
                                                             title,
                                                             service_name,
                                                             service_suggest)
                    run_service_id = self.dao.get_car_run_service_id(self.source_id,
                                                                     response.meta['car_id'],
                                                                     response.meta['firsttime'],
                                                                     response.meta['mile'],
                                                                     service_id,
                                                                     type,
                                                                     car_suggest)
                    second_value_list = second_value.split('-')
                    for one_second_value in second_value_list:
                        p_name_service_id_map[source_service_id + '_' + one_second_value] = run_service_id
        meta = response.meta
        meta['service_list'] = service_value_list
        meta['next_service'] = 1
        meta['p_name_service_id_map'] = p_name_service_id_map
        timestamp = str(int(time.time()))
        return ants.Request(
            self.add_service_url + 'itemids=' + ','.join(
                service_value_list[0]) + ',&_=' + timestamp + '&jar=' + str(
                meta['cookiejar']),
            meta=meta,
            callback='add_service')

    def add_service(self, response):
        meta = response.meta
        if meta['next_service'] >= len(meta['service_list']):
            return ants.Request(
                'http://www.yangche51.com/baoyang/step3.html?curmileage=' + str(meta['mile']) + '&firsttime=' +
                meta[
                    'firsttime'] + '&jar=' + str(meta['cookiejar']),
                meta=response.meta,
                callback='parse_service_goods')
        next_service = meta['next_service']
        meta['next_service'] += 1
        timestamp = str(int(time.time()))
        return ants.Request(
            self.add_service_url + 'itemids=' + ','.join(
                meta['service_list'][next_service]) + ',&_=' + timestamp + '&jar=' + str(
                meta['cookiejar']),
            meta=meta,
            callback='add_service')

    def parse_service_goods(self, response):
        tr_list = response.xpath('//div[@class="tableBox"]/table/tr')
        meta = response.meta
        for tr in tr_list[2:]:
            name = tr.xpath('./td[@class="pDo"]/i/@data').extract()
            if not name:
                continue
            name = name[0]
            href = tr.xpath('./td[contains(@class,"pLink")]/a/@href').extract()
            if not href:
                continue
            href = href[0]
            source_goods_id = href[self.front_len:].split('.')[0]
            sql = 'select id from dw_crawl_goods where source_id = ' + str(
                self.source_id) + ' and source_goods_id = "' + source_goods_id + '"'
            goods_id_data = self.dao.db.get_data(sql)
            goods_id = None
            if goods_id_data:
                goods_id = goods_id_data[0]['id']
            else:
                yield ants.Request(self.front_url + source_goods_id + '.html', callback='parse_goods')
            service_id = meta['p_name_service_id_map'][name]
            self.dao.add_car_run_service_goods(self.source_id, service_id, source_goods_id, goods_id)


    front_url = 'http://item.yangche51.com/p-'

    front_len = len(front_url)

    add_service_url = 'http://www.yangche51.com/handlers/maintenance/maintenanceprovider.ashx?action=addmaintenlist&'

    def parse_goods(self, response):
        source_goods_id = response.url[28:].split('.')[0]
        title = response.xpath('//div[@class="protitle"]/dl/dt/h1/text()').extract()[0].strip()
        brand = response.xpath('//div[@class="crumb"]/text()')[2].extract().replace('>', '').strip().split()[0]
        image = response.xpath('//ul[@id="JQ-slide-content"]/div/img/@src').extract()[0]
        cate_a = response.xpath('//div[@class="crumb"]/a')[2]
        cate_name = cate_a.xpath('./text()').extract()[0].strip()
        source_cate_id = cate_a.xpath('./@href').extract()[0][34:].split('.')[0]
        cate_id = self.dao.get_cate_id_by_name(source_cate_id, self.source_id, cate_name)
        db_dict = dict()
        db_dict['source_id'] = self.source_id
        db_dict['cate_id'] = cate_id
        db_dict['brand_id'] = self.dao.get_brand_id(self.source_id, brand)
        db_dict['source_goods_id'] = source_goods_id
        db_dict['title'] = title
        db_dict['image'] = image
        goods_id = self.dao.insert_or_update_template('dw_crawl_goods', db_dict, CrawlDao.db_goods_unique_key)
        sql = 'update dw_crawl_car_run_service_goods set goods_id=' + str(
            goods_id) + ' where source_goods_id="' + source_goods_id + '"'
        self.dao.db.exec_data(sql)



