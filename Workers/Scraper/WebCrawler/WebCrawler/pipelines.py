# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class WebcrawlerPipeline:
    def process_item(self, item, spider):
        Adaptor = ItemAdapter(item)

        if Adaptor.get('title'):
            Adaptor['title'] = Adaptor['title'].strip()

        if Adaptor.get('link') and not Adaptor['link'].startswith('http'):
            Adaptor['link'] = spider.start_urls[0] + Adaptor['link']

        return item
