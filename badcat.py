# -*- coding: utf-8 -*-
# import scrapy
# import sys
# # from scrapy.contrib.linkextractors import LinkExtractor 弃用
# from scrapy.linkextractors import LinkExtractor
# from scrapy.spiders import CrawlSpider,Rule
# from discuz.items import DiscuzItem

# reload(sys)
# sys.setdefaultencoding("utf-8")


# class BadcatSpider(CrawlSpider):
#     name = 'badcat'
#     allowed_domains = ['s8beta.com']
#     start_urls = [
#         "http://s8beta.com/forum.html",
#         # "http://s8beta.com/forum-282-1.html",
#     ]
#     rules = (
#         # Rule(LinkExtractor(allow=(r'http://s8beta.com/'),)),
#         # Rule(LinkExtractor(allow=(r'http://s8beta.com/forum-282-1.html'),)),
#         # Rule(LinkExtractor(allow=(r'http://s8beta.com/forum-282-[1,2,3].html',)),callback = 'parse_list'),
#         Rule(LinkExtractor(allow=(r'http://s8beta.com/forum-(\d+)-1.html',)),callback = 'parse_list'),
#     )
#     def parse_list(self, response):
#         item = DiscuzItem()
#         # item['name'] = response.selector.xpath('//*[@id="ct"]/div/*/h1[@class="xs2"]/a/text()')[0].extract().decode('utf-8')
#         item['name'] = response.selector.xpath('//h1[@class="xs2"]/a/text()')[0].extract().decode('utf-8')
#         item['url'] = response.selector.xpath('//h1[@class="xs2"]/a/@href').extract()[0]


#         yield item


import scrapy
from discuz.items import DiscuzItem
class BadcatSpider(scrapy.Spider):
  # 定义爬虫的名称，主要main方法使用
  name = 'badcat'
  allowed_domains = ["douban.com"]
  start_urls = [
    "http://movie.douban.com/top250/"
  ]
  # 解析数据
  def parse(self, response):
    items = []
    for info in response.xpath('//div[@class="item"]'):
      item = DiscuzItem()
      item['rank'] = info.xpath('div[@class="pic"]/em/text()').extract()
      item['title'] = info.xpath('div[@class="pic"]/a/img/@alt').extract()
      item['link'] = info.xpath('div[@class="pic"]/a/@href').extract()
      item['rate'] = info.xpath('div[@class="info"]/div[@class="bd"]/div[@class="star"]/span/text()').extract()
      item['quote'] = info.xpath('div[@class="info"]/div[@class="bd"]/p[@class="quote"]/span/text()').extract()
      items.append(item)
      yield item
    # 翻页
    next_page = response.xpath('//span[@class="next"]/a/@href')
    if next_page:
      url = response.urljoin(next_page[0].extract())
      #爬每一页
      yield scrapy.Request(url, self.parse)        
