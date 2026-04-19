import re
from pathlib import Path
from urllib.parse import urlparse
import scrapy
from Crawler.items import CrawlerItem
from Crawler.utils.UniLinkMap import UniLinkMap as UniLinkmap
from Crawler.utils.filter import filter
import json
from Crawler.utils.Cleaner import converter

class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = [
        "usa.edu.pk",
        "bzu.edu.pk",
        "lahoreschoolofeconomics.edu.pk",
        "ucp.edu.pk",
        "wum.edu.pk",
        "numl.edu.pk",
        "iqra.edu.pk",
        "uop.edu.pk",
        "vu.edu.pk",
        "uol.edu.pk",
        "muet.edu.pk",
        "szabist.edu.pk",
        "fccollege.edu.pk",
        "su.edu.pk",
        "uswat.edu.pk",
        "gcuf.edu.pk",
        "iobm.edu.pk",
        "iub.edu.pk",
        "usindh.edu.pk"
    ]

    start_urls = [
        "https://usa.edu.pk/",
        "https://bzu.edu.pk/",
        "https://www.lahoreschoolofeconomics.edu.pk/",
        "https://ucp.edu.pk/",
        "https://wum.edu.pk/",
        "https://numl.edu.pk/",
        "https://iqra.edu.pk/",
        "http://www.uop.edu.pk/",
        "https://www.vu.edu.pk/",
        "https://uol.edu.pk/",
        "https://www.muet.edu.pk/",
        "https://szabist.edu.pk/",
        "https://www.fccollege.edu.pk/",
        "https://su.edu.pk/",
        "https://uswat.edu.pk/",
        "https://gcuf.edu.pk/",
        "https://iobm.edu.pk/",
        "https://www.iub.edu.pk/",
        "https://usindh.edu.pk/"
    ]

    SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".svg",
                ".css", ".js", ".zip", ".rar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()
        self.pdf_urls = []

    def parse(self, response):
        data = []

        for a in response.css("a"):
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
                continue
            self.seen_links.add(url)

            # extract readable anchor text
            text_parts = [t.strip() for t in a.css("::text").getall()]
            title = " ".join([p for p in text_parts if p]).strip() or "no title"

            data.append({
                "title": title,
                "link": url
            })


        #here we would filter the links to only top 10 links

        used_links = filter(data)

        #yield {"links": used_links}

        used_data = [d for d in data if d["link"] in used_links]

        remaining_data = [d for d in data if d["link"] not in used_links]  

        for link in remaining_data:
            item = CrawlerItem()
            item["title"] = link["title"]
            item["link"] = link["link"]
            item["uni"] = UniLinkmap[response.url]
            item["save_dir"] = "None"
            yield item

        for link in used_data:
            yield response.follow(link["link"], callback=self.parse2, 
                                  meta={
                                      "uni": UniLinkmap[response.url],
                                      "title": link["title"],
                                      "link": link["link"]
                                      })


    def parse2(self, response):
        dir = converter(response,response.meta["uni"])

        item = CrawlerItem()
        item["title"] = response.meta["title"]
        item["link"] = response.meta["link"]
        item["uni"] = response.meta["uni"]
        item["save_dir"] = dir
        yield item

        for a in response.css("a"):
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
                continue
            self.seen_links.add(url)

            # extract readable anchor text
            text_parts = [t.strip() for t in a.css("::text").getall()]
            title = " ".join([p for p in text_parts if p]).strip() or "no title"

            item = CrawlerItem()
            item["title"] = title
            item["link"] = url
            item["uni"] = response.meta["uni"]
            item["save_dir"] = "None"
            yield item

            links = response.css("a::attr(href)").getall()
            for link in links:
                full_url = response.urljoin(link)
                if full_url.lower().endswith(".pdf"):
                    self.pdf_urls.add({
                        "link": full_url,
                        "uni": response.meta["uni"]
                    })
           
    def closed(self, reason):
        with open("pdf_urls.json", "w", encoding="utf-8") as f:
            json.dump(list(self.pdf_urls), f, indent=4)

        path = Path(__file__).parent.parent.parent.parent / "Crawler" / "cleaned_pages"

        folders = [f for f in path.iterdir() if f.is_dir()]

        with open("prev_scanned_unis.json", "w", encoding="utf-8") as f:
            json.dump(folders,f,indent=4)

        with open("left_unis.json", "w", encoding="utf-8") as f:
            json.dump(folders,f,indent=4)

        # #here we would add 10 more links

        # used_links = []

        # for link in used_links:
        #     yield response.follow(link, callback=self.parse2)

