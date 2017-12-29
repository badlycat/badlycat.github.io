# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class DiscuzPipeline(object):
#     def process_item(self, item, spider):
#         return item

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import MySQLdb

class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost','root','','demo',charset='utf8',use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self,item,spider):
        insert_sql = """
            insert into test (name,url) values(%s,%s)
        """
        self.cursor.execute(insert_sql,(item['name'],item['url']))
        self.cursor.commit()

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

class MysqlTwistPipeline(object):
    # 名称固定 会被scrapy调用，使用settong配置的值
    def from_setting(cls,settings):
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
            )
    """docstring fos MysqlTwistPipeline"""
    def __init__(self, dbpool):
        self.dbpool = dbpool


    def process_item(self,item,spider):
        # 使用twiset将mysql插入变成异步
        query = self.dbpool.runInteraction(self.do_insert,item)
        # 因为异步，可能有些错误不能及时报出
        query.addErrback(self.handle_error)

    def handle_error(self,failure):
        print('failure')

    def do_insert(self,cursor,item):
        insert_sql = """
            insert into test (name,url) values(%s,%s)
        """
        cursor.execute(insert_sql,(item['name'],item['url']))


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import json
# import codes
import codecs
class JsonCodesPipeline(object):
    def __init__(self):
        self.file = codecs.open('douban.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
    def spider_closed(self, spider):
        self.file.close()

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#将数据存储到mysql数据库
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
class MySQLStorePipeline(object):
    #数据库参数
    def __init__(self):
        dbargs = dict(
             host = '127.0.0.1',
             db = 'demo',
             user = 'root',
             passwd = '',
             cursorclass = MySQLdb.cursors.DictCursor,
             charset = 'utf8',
             use_unicode = True
            )
        self.dbpool = adbapi.ConnectionPool('MySQLdb',**dbargs)

    '''
    The default pipeline invoke function
    '''
    def process_item(self, item,spider):
        res = self.dbpool.runInteraction(self.insert_into_table,item)
        return item
    #插入的表，此表需要事先建好
    def insert_into_table(self,conn,item):
            conn.execute('insert into douban(rank, title, rate,quote,link) values(%s,%s,%s,%s,%s)', (
                item['rank'][0],
                item['title'][0],
                # item['star'][0],
                item['rate'][0],
                item['quote'][0],
                item['link'][0])
                )
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 图片下载处理
import requests
from discuz import settings
import os

class ImageDownLoadPipeline(object):
    def process_item(self,item,spider):
        if 'image_urls' in  item:
            images = []
        
        dir_path = '%s%s' % (settings.IMAGES_STORE,spider.name)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for image_url in item['image_urls']:
            us = image_url.split('/')[3:]
            image_file_name = '_'.join(us)
            file_path = '%s%s' %  (dir_path,image_file_name)
            images.append(file_path)
            if os.path.exists(file_path):
                continue

        with open(file_path,'wb') as handle:
            response = requests.get(image_url,stream = True)
            for block in response.iter_content(1024)
             if not block:
                break
