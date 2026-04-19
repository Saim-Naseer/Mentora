from importlib.resources import path
import re
from pathlib import Path
import shutil
from urllib.parse import urlparse
import scrapy
from Crawler.items import CrawlerItem
from Crawler.utils.UniLinkMap import UniLinkMap as UniLinkmap
from Crawler.utils.filter import filter2
from Crawler.utils.Cleaner import converter
import json

class SpiderSpider(scrapy.Spider):
    name = "spider2"
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

    SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".svg",
                ".css", ".js", ".zip", ".rar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pdf_urls = []

        folder = Path("cleaned_pages")

        for item in folder.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        self.start_urls = []
        filepath = Path("out.json")
        f = open(filepath, "r", encoding="utf-8")
        self.data = json.load(f)
        f.close()

        # unseen_links = [d["link"] for d in data if d["save_dir"]=="None"]

        # for link in unseen_links:
        #     self.start_urls.append(link)

        uni_jsons_path = Path(__file__).parent.parent.parent.parent / "Extractor" / "final_data.json"
        f = open(uni_jsons_path, "r", encoding="utf-8")
        uni_json_list = json.load(f)
        f.close()

        path = Path(__file__).parent.parent.parent / "prev_scanned_unis.json"

        file = open(path,"r",encoding="utf-8")
        folders = json.load(file)

        for k in [str(f).split("\\")[-1] for f in folders]:
            uni_unseen_links = [d["link"] for d in self.data if d["uni"]==k and d["save_dir"]=="None"]
            uni_seen_links = [d["link"] for d in self.data if d["uni"]==k and d["save_dir"]!="None"]
            print("at uni", k)
            uni_json = [d for d in uni_json_list if d["uni"]==k][0]["object"]

            filtered_links = filter2(uni_unseen_links,uni_seen_links, uni_json)
            self.start_urls.extend(filtered_links)

        
    def parse(self, response):
        uni = [d for d in self.data if d["link"]==response.url][0]["uni"]
        
        if not response.url.lower().endswith(".pdf"):
            save_dir = converter(response, uni)
            item = CrawlerItem()
            item["title"] = "No Title"
            item["link"] = response.url
            item["uni"] = uni
            item["save_dir"] = save_dir
            yield item

        # Extract links
        links = response.css("a::attr(href)").getall()
        for link in links:
            full_url = response.urljoin(link)
            if full_url.lower().endswith(".pdf"):
                self.pdf_urls.append({
                    "link": full_url,
                    "uni": uni
                })
           
    def closed(self, reason):
        data=[]

        try:
            with open("pdf_urls.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            data = []
            print("saim")
            print(e)

        old = [d["link"] for d in data]

        for i in self.pdf_urls:
            if i["link"] not in old:
                data.append(i)

        with open("pdf_urls.json", "w", encoding="utf-8") as f:
            json.dump(list(data), f, indent=4)