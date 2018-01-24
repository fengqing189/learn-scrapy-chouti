# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.http.cookies import CookieJar


class Chouti2Spider(scrapy.Spider):
    name = 'chouti2'
    allowed_domains = ['chouti.com']
    start_urls = ['http://chouti.com/']

    cookie_dict = {}

    def start_requests(self):
        yield scrapy.Request('http://dig.chouti.com/', callback=self.login)

    def login(self, response):
        '''发送ajax请求来登录'''

        # 从response中拿到cookie信息

        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response, response.request)

        # for k, v in cookie_jar._cookies.items():
        #     for i, j in v.items():
        #         for m, n in j.items():
        #             self.cookie_dict[m] = n.value

        login_req = Request(
            url='http://dig.chouti.com/login',
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
            body='phone=8618922795525&password=woaiwojia89&oneMonth:1',
            cookies=self.cookie_dict,
            callback=self.check_login,
        )
        print(self.cookie_dict)
        print('执行了login')
        yield login_req

    def check_login(self, response):
        '''拿到登录的状态'''
        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response, response.request)
        for k, v in cookie_jar._cookies.items():
            for i, j in v.items():
                for m, n in j.items():
                    self.cookie_dict[m] = n.value

        req = Request(
            url='http://dig.chouti.com/',
            method='GET',
            cookies=self.cookie_dict,
            dont_filter=True,
            callback=self.index_page,
        )
        print('执行了check_login')
        yield req

    def index_page(self, response):
        '''拿到登陆之后的页面'''
        # 1.点赞功能
        # content_id_list = response.xpath('//*[@class="content-list"]//*[@class="part2"]/@share-linkid').extract()
        # base_url = 'http://dig.chouti.com/link/vote?linksId=%s'
        # for link_id in content_id_list:
        #     up_req = Request(url=base_url % link_id,
        #             method='POST',
        #             cookies=self.cookie_dict,
        #             callback = self.do_faver,
        #             dont_filter=True,
        #             )
        #     yield up_req


        # 2.拿到当前页面每个内容的title，点赞数up_num、评论数comment_num
        from ..items import ChoutiItem
        content_items = response.xpath('//*[@class="content-list"]//*[@class="item"]')
        print('++++++=========',content_items)

        for each_item in content_items:
            title = each_item.xpath('.//*[@class="part2"]/@share-title').extract_first()
            up_num = each_item.xpath('.//*[@class="part2"]/a[@class="digg-a"]/b/text()').extract_first()
            comment_num = each_item.xpath('.//*[@class="part2"]/a[@class="discus-a"]/b/text()').extract_first()

            item = ChoutiItem(title=title, up_num=up_num, comment_num=comment_num)
            yield item


        # 找到下一页,点击，拿到页面，在执行这个函数
        # next_page = response.css('.ct_page_edge::attr(href)').extract_first()
        next_page = response.xpath('//*[@id="dig_lcpage"]//a/@href').extract()[-1]
        new_text = response.xpath('//*[@id="dig_lcpage"]//a/text()').extract()[-1]
        if new_text == '下一页':
            next_page_url = response.urljoin(next_page)

            next_page_req = Request(
                url=next_page_url,
                cookies=self.cookie_dict,
                callback=self.index_page,
                dont_filter=True,
                )

            yield next_page_req



    def do_faver(self,response):
        print('%s 已经点赞'%response.url)