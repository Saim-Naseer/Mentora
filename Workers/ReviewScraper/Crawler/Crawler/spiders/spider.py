import re
from pathlib import Path
from urllib.parse import urlparse
import scrapy
from Crawler.items import CrawlerItem, ReviewItem
import json


class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["eduopinions.com"]
    start_urls = []

    SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".svg",
                ".pdf", ".css", ".js", ".zip", ".rar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()
        json_path = Path(__file__).resolve().parents[2] /"UniList"/"urls2.json"

        f = open(json_path, "r", encoding="utf-8")
        data = json.load(f)
        self.start_urls = data
        f.close()

    def parse(self, response):
        for a in response.css("div.programmes-wrapper a"):
            href = a.attrib.get("href")
            if not href:
                continue

            if href.startswith(("mailto:", "javascript:", "tel:")) or href.startswith("#"):
                continue

            # normalize to absolute url and strip fragment
            url = response.urljoin(href).split("#", 1)[0].strip()
            if not url:
                continue

            # quick filter on common static file extensions
            url_path = url.split("?", 1)[0].lower()
            if any(url_path.endswith(ext) for ext in self.SKIP_EXT):
                continue

            # in-memory dedupe (avoid scheduling same URL multiple times)
            if url in self.seen_links:
                self.logger.debug("already exists: %s", url)
                continue
            self.seen_links.add(url)

            title = (response.css("span.uniName::text").get() or "").strip()

            yield response.follow(url, callback=self.parse2, meta={"uni":title})

    def parse2(self, response):

        for a in response.css("ul > li.opinions-item.clearfix"):
            university = response.meta.get("uni", "unknown")
            text = a.css("div.opinionBody p::text").getall()
            text = " ".join([t.strip() for t in text if t.strip()])
            programme = a.xpath("normalize-space(.//span[contains(text(),'Programme')]/following-sibling::text())").get() or ""
            degree = a.xpath("normalize-space(.//span[contains(text(),'Degree')]/following-sibling::text())").get() or ""
            graduation = a.xpath("normalize-space(.//span[contains(text(),'Graduation')]/following-sibling::text())").get() or ""
            delivery_type = a.xpath("normalize-space(.//span[contains(text(),'Delivery Type')]/following-sibling::text())").get() or ""
            campus = a.xpath("normalize-space(.//span[contains(text(),'Campus')]/following-sibling::text())").get() or ""

            ratings = {}

            for div in a.css("div.rating"):
                label = div.css("span:not(.opinion-stars)::text").get()
                stars = div.css("span.opinion-stars::attr(data-rating)").get()
                if label and stars:
                    ratings[label.strip()] = int(float(stars))

            item = ReviewItem()
            item["university"] = university
            item["text"] = text if text else ""
            item["programme"] = programme if programme else ""
            item["degree"] = degree if degree else ""
            item["graduation"] = graduation if graduation else ""
            item["delivery_type"] = delivery_type if delivery_type else ""
            item["campus"] = campus if campus else ""
            item["overall_rating"] = ratings.get("Overall", 0)
            item["professors_rating"] = ratings.get("Professors", 0)
            item["internationality_rating"] = ratings.get("Internationality", 0)
            item["career_prospects_rating"] = ratings.get("Career Prospects", 0)
            item["value_rating"] = ratings.get("Value", 0)
            item["location_rating"] = ratings.get("Location", 0)
            item["facilities_rating"] = ratings.get("Facilities", 0)
            item["accommodation_rating"] = ratings.get("Accommodation", 0)
            item["student_life_rating"] = ratings.get("Student Life", 0)
            yield item

