import scrapy


class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(self, response):
        pass
