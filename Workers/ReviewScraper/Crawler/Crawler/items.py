# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    title=scrapy.Field()
    link=scrapy.Field()
    save_dir = scrapy.Field()
    pass

class ReviewItem(scrapy.Item):
    university=scrapy.Field()
    text=scrapy.Field()
    programme=scrapy.Field()
    graduation=scrapy.Field()
    degree=scrapy.Field()
    delivery_type=scrapy.Field()
    campus=scrapy.Field()
    overall_rating=scrapy.Field()
    professors_rating=scrapy.Field()
    internationality_rating=scrapy.Field()
    career_prospects_rating=scrapy.Field()
    value_rating=scrapy.Field()
    location_rating=scrapy.Field()
    facilities_rating=scrapy.Field()
    accommodation_rating=scrapy.Field()
    student_life_rating=scrapy.Field()
    pass