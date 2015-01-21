# encoding=utf8
__author__ = 'wcong'
import ants


class FengLianGoodsSpider(ants.Spider):
    name = 'feng_lian_goods'
    start_urls = [
        'http://23255555.com/index.html'
    ]


    def parse(self, response):
        first_cate_list = response.xpath('//div[@id="SNmenuNav"]/dl')
        for first_cate in first_cate_list:
            first_cate_name = first_cate.xpath('./dt/a/text()').extract()[0].strip()
            second_cate_list = first_cate.xpath('./dd/ul/li/div/a')
            for second_cate in second_cate_list:
                second_cate_name = second_cate.xpath('./@title').extract()[0]
                link = second_cate.xpath('./@href').extract()[0]
                yield ants.Request(link,
                                   meta={'first_cate_name': first_cate_name,
                                         'second_cate_name': second_cate_name},
                                   callback=self.parse_list)

    def parse_list(self, response):
        goods_list = response.xpath('//ul[@id="faq"]/li/div[@class="listshow"]')
        for goods in goods_list:
            goods_id = goods.xpath('./div[@class="W_2"]/a/text()').extract()[0].strip()
            url = 'http://23255555.com/shop/detail/' + goods_id + '.html'
            yield ants.Request(url, meta=response.meta, callback=self.parse_goods)

        classifyId = response.xpath('//input[@id="classifyId"]/@value').extract()[0]
        page_size = response.xpath('//input[@id="pageSize"]/@value').extract()[0]
        meta = response.meta
        if 'page_num' not in meta:
            meta['page_num'] = 1
        if len(goods_list) == int(page_size):
            meta['page_num'] += 1
            # print meta['page_num']
            response.xpath('//listForm')
            formdata = {'pageclickednumber': str(meta['page_num']),
                        'pageSize': page_size,
                        'classifyId': classifyId}
            yield ants.FormRequest(response.url, meta=meta, formdata=formdata, callback=self.parse_list)

    def parse_goods(self, response):
        meta = response.meta
        try:
            image = response.xpath('//img[@id="focpic"]/@src').extract()[0]
        except Exception, e:
            image = ''
        goods_title = response.xpath('//div[@class="Prod_detail_T1 W600"]/text()').extract()[0].strip()
        first_attr_list = response.xpath('//div[@class="Rinfobox"]/div[contains(@class,"infoline")]')
        for first_attr in first_attr_list:
            header = first_attr.xpath('./span[@class="info_header"]/text()').extract()[0].strip()
            if header.find('产品编号') > -1:
                goods_id = first_attr.xpath('./text()').extract()[1].strip()
            elif header.find('产品品牌') > -1:
                brand_name = first_attr.xpath('./text()').extract()[1].strip()
        # TODO for now it is complicate
        # car_info = first_attr_list[4].xpath('./div/div[@class="w4tip_box"]/text()').extract()[0].strip().split('.')
        second_attr_list = response.xpath('//div[@class="Prod_detail_conbox"]/text()').extract()
        filter_attr_key = ['配件名称', '类型描述', '促销信息', '货品详细描述']
        data = dict()
        for second_attr in second_attr_list:
            attr_list = second_attr.strip().split('：')
            attr_key = attr_list[0].strip()
            if len(attr_list) < 2:
                continue
            attr_value = attr_list[1].strip()
            if attr_key in filter_attr_key:
                continue
            if attr_key == '适用车型':
                # TODO for now it is complicate
                continue
            if attr_key in self.attr_map:
                data[self.attr_map[attr_key]] = attr_value
            else:
                print 'none attr key:' + attr_key

        data['first_cate_name'] = meta['first_cate_name']
        data['second_cate_name'] = meta['second_cate_name']
        data['image'] = image
        data['title'] = goods_title
        data['source_goods_id'] = goods_id
        data['brand_name'] = brand_name

    attr_map = {
        'OE码'.decode("utf8"): 'oe',
        '单位'.decode("utf8"): 'unit',
        '长(mm)'.decode("utf8"): 'length',
        '宽(mm)'.decode("utf8"): 'width',
        '高(mm)'.decode("utf8"): 'height',
        '重量(g)'.decode("utf8"): 'weight'
    }
