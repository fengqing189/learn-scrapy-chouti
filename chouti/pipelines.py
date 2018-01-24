# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from pymongo import MongoClient

class ChoutiPipeline(object):
    def __init__(self, db_name, collection, user, pwd, ip, port):

        self.db_name= db_name
        self.collection = collection
        self.user = user
        self.pwd = pwd
        self.ip = ip
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        """
        Scrapy会先通过getattr判断我们是否自定义了from_crawler,有则调它来完
        成实例化
        """
        db_name = crawler.settings.get('DB_NAME')
        collection = crawler.settings.get('COLLECTION')
        user = crawler.settings.get('USER')
        pwd = crawler.settings.get('PWD')
        ip = crawler.settings.get('IP')
        port = crawler.settings.get('PORT')
        return cls(db_name,collection,user,pwd,ip,port)

    def open_spider(self,spider):
        """
        爬虫刚启动时执行一次,建立数据库的链接
        """
        print('%s爬虫开始了'%spider.name)
        self.client = MongoClient(r'mongodb://%s:%s@%s:%s/'%(self.user,self.pwd,self.ip,self.port))


    def process_item(self, item, spider):
        d = dict(item)
        self.client[self.db_name][self.collection].save(d)

        # return表示会被后续的pipeline继续处理
        return item


    def close_spider(self,spider):
        """
        爬虫关闭时执行一次
        """
        print('%s爬虫结束了' % spider.name)

        # 表示将item丢弃，不会被后续pipeline处理
        # raise DropItem()