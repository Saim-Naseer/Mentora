import requests
from bs4 import BeautifulSoup, Comment


url = "https://edurank.org/uni/harvard-university/"
resp = requests.get(url, timeout=10)
resp.raise_for_status()            
html = resp.text       

soup = BeautifulSoup(html, "html.parser")

full_html = soup.prettify()

with open("test.html", "w", encoding="utf-8") as f:
    f.write(full_html)
