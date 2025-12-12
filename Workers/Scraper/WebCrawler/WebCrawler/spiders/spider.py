import re
from pathlib import Path
from urllib.parse import urlparse
import scrapy
from WebCrawler.items import WebcrawlerItem


class SpiderSpider(scrapy.Spider):
    name = "spider"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

   SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".svg",
                ".pdf", ".css", ".js", ".zip", ".rar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()
        self.base_dir = Path("pages")         # base folder where the tree will be written
        self.base_dir.mkdir(exist_ok=True)

    def safe_name(self, url: str, maxlen: int = 150) -> str:
        """Create a filesystem-safe short name from a URL for folder names."""
        p = urlparse(url)
        name = (p.netloc + p.path).rstrip("/")
        # replace non-alnum with underscore and collapse multiple underscores
        name = re.sub(r"[^0-9A-Za-z\-_.]", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")
        if not name:
            name = "root"
        return name[:maxlen]

    def parse(self, response):
        # Determine this page's folder to save into (meta['save_dir'] provided when following)
        current_save_dir = Path(response.meta.get("save_dir", str(self.base_dir)))
        current_save_dir.mkdir(parents=True, exist_ok=True)

        # Save the HTML of the page as index.html inside its folder
        file_path = current_save_dir / "index.html"
        try:
            file_path.write_bytes(response.body)
            self.logger.info("Saved page: %s", file_path)
        except Exception as e:
            self.logger.warning("Failed to save %s: %s", file_path, e)

        # Now extract links and prepare children folders; schedule follows with save_dir meta
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
                self.logger.debug("already exists: %s", url)
                continue
            self.seen_links.add(url)

            # compute a safe child folder inside the current_save_dir for this URL
            child_folder_name = self.safe_name(url)
            child_save_dir = current_save_dir / child_folder_name

            # extract readable anchor text
            text_parts = [t.strip() for t in a.css("::text").getall()]
            title = " ".join([p for p in text_parts if p]).strip() or "no title"

            # yield WebcrawlerItem (optional) - include where we plan to save the HTML
            item = WebcrawlerItem()
            item["title"] = title
            item["link"] = url
            item["save_dir"] = str(child_save_dir)   # helpful for later reference
            yield item

            # follow child page and tell parse where to save it
            yield response.follow(url, callback=self.parse, meta={"save_dir": str(child_save_dir)})

