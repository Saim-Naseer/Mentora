# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title=scrapy.Field()
    link=scrapy.Field()
    uni=scrapy.Field()
    save_dir=scrapy.Field()
    pass


class CrawlerItem2(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link=scrapy.Field()
    uni=scrapy.Field()
    text=scrapy.Field()
    pass