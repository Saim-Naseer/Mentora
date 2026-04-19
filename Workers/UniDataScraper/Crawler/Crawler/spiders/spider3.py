import scrapy
from pathlib import Path
import json
from Crawler.utils.filter import filter3
from Crawler.utils.UniLinkMap import UniLinkMap
from Crawler.items import CrawlerItem2
import fitz  # PyMuPDF
from PIL import Image
import base64
from io import BytesIO
from dotenv import load_dotenv
import os
from groq import Groq
from urllib.parse import unquote


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def normalize_url(url):
    return unquote(url).strip()

class SpiderSpider(scrapy.Spider):
    name = "spider3"
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

    custom_settings = {
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 1,         
        "DOWNLOAD_TIMEOUT": 450
    }

    SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".css", ".js", ".zip", ".rar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = []

        filepath = Path("pdf_urls.json")
        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        path = Path(__file__).parent.parent.parent / "prev_scanned_unis.json"

        file = open(path,"r",encoding="utf-8")
        folders = json.load(file)

        for uni in [str(f).split("\\")[-1] for f in folders]:
            if uni == "USINDH":
                continue
            pdf_urls = [d["link"] for d in self.data if d["uni"] == uni]
            if pdf_urls:
                selected_urls = filter3(pdf_urls)
                self.start_urls.extend(selected_urls)
                with open("selected_pdf_urls.json", "a", encoding="utf-8") as f:
                    json.dump(selected_urls, f, indent=4)

        

    def parse(self, scrapy_response):
        doc = fitz.open(stream=scrapy_response.body, filetype="pdf")

        all_text = []

        try:
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                buffer = BytesIO()
                img.save(buffer, format="JPEG")
                base64_image = base64.b64encode(buffer.getvalue()).decode()

                groq_response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extract all structured information from this page."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                )

                content = groq_response.choices[0].message.content
                if isinstance(content, list):
                    content = "".join([c.get("text", "") for c in content])

                all_text.append(content)

            final_output = "\n".join(all_text)

            uni_matches = [d["uni"] for d in self.data if normalize_url(d["link"]) == normalize_url(scrapy_response.url)]
            uni = uni_matches[0] if uni_matches else "Unknown"

            if uni == "Unknown":
                u=scrapy_response.url.replace(" ","")
                count=0
                for s in u:
                    if count==2:
                        continue
                    if count==1 and s!='/':
                        continue
                    if s=="/":
                        count+=1
                    u=u[1:]
                    
                for d in data:

                    temp = d["link"].replace(" ","")
                    if u in temp:
                        uni = d["uni"]

            if uni != "Unknown":
                print("\n\n\n\n=======================================================")
                print(uni)
                print("=======================================================\n\n\n\n")

                item = CrawlerItem2()
                item["link"] = scrapy_response.url
                item["uni"] = uni
                item["text"] = final_output
                yield item
                
        except Exception as e:
            with open("error.log","a",encoding="utf-8") as f:
                f.write("ERROR : \n",e,"\n\n")
        finally:
            doc.close()