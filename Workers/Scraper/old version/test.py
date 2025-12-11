# pip install requests beautifulsoup4 lxml
import re
import requests
from bs4 import BeautifulSoup, Comment

REMOVE_CLASS_KEYWORDS = [
    'sidebar','advert','ads','cookie','consent','promo','newsletter','signup',
    'footer','header','nav','breadcrumb','related','recommended','subscribe',
    'popup','modal','cookie-banner','sponsored'
]

def fetch_html(url, timeout=10):
    r = requests.get(url, timeout=timeout, headers={'User-Agent':'Mozilla/5.0'})
    r.raise_for_status()
    return r.text

def remove_nodes_by_keyword(soup):
    # remove by tag name
    for tag in soup(['script','style','noscript','iframe','svg','canvas','form','input','button']):
        tag.decompose()
    # remove comments
    for c in soup.find_all(text=lambda t: isinstance(t, Comment)):
        c.extract()
    # remove nodes by class/id heuristics
    for el in soup.find_all(True):
        cls = ' '.join(el.get('class') or [])
        id_ = el.get('id') or ''
        attrs = f"{cls} {id_}".lower()
        if any(k in attrs for k in REMOVE_CLASS_KEYWORDS):
            el.decompose()

def strip_attributes(soup):
    for tag in soup.find_all(True):
        # remove all attributes except allowlist for anchors & images
        allow = {}
        if tag.name == 'a' and tag.get('href'):
            allow = {'href': tag['href']}
        if tag.name == 'img' and tag.get('src'):
            allow = {'src': tag['src'], 'alt': tag.get('alt','')}
        tag.attrs = allow

def keep_main_text(soup):
    # naïve main content extraction: choose largest block of text
    candidates = []
    for tag in soup.find_all(['article','main','section','div']):
        text = tag.get_text(separator=' ', strip=True)
        candidates.append((len(text), tag))
    if not candidates:
        return soup.get_text(separator='\n', strip=True)
    largest = max(candidates, key=lambda x: x[0])[1]
    return largest.get_text(separator='\n\n', strip=True)

def normalize_text(text):
    text = text.replace('\xa0',' ')  # non-breaking
    text = re.sub(r'\n{3,}', '\n\n', text)  # collapse newlines
    text = re.sub(r'[ \t]{2,}', ' ', text)  # collapse spaces
    text = re.sub(r'[-=]{3,}', '', text)  # remove long separators
    text = re.sub(r'([\.\?!]){2,}', r'\1', text)  # repeated punctuation
    return text.strip()

def extract_clean_text(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, 'lxml')
    remove_nodes_by_keyword(soup)
    strip_attributes(soup)
    main_text = keep_main_text(soup)
    return normalize_text(main_text)

file = open("harvard_homepage.html", "r", encoding="utf-8")

with open("harvard_cleaned.txt", "w", encoding="utf-8") as out_file:
    out_file.write(extract_clean_text(file.read()))
