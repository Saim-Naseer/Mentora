from html_to_markdown import convert
from bs4 import BeautifulSoup
import os
from pathlib import Path

def clean_html(f):
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    for tag in ["script", "style","link"]:
        for t in soup.find_all(tag):
            t.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.Comment))):
        comment.extract()

    for tag in soup.find_all():
        if not tag.get_text(strip=True) and not tag.name in ["br", "hr"]:
            tag.decompose()

    for tag in soup.find_all(True):
        if 'class' in tag.attrs:
            del tag.attrs['class']

    # for tag in soup.find_all(string=True):
    #     tag.replace_with(re.sub(r"\s+", " ", tag))
    return str(soup)


def converter(files):
    i=1
    for file in files:
        infile = open(file, "r", encoding="utf-8")
        data = clean_html(infile)

        markdown = convert(data)
        if isinstance(markdown, bytes):
            markdown = markdown.decode("utf-8")

        if os.path.exists("cleaned_pages/"+file.split("/")[-2]):
            os.remove("cleaned_pages/"+file.split("/")[-2])

        outfile = open("cleaned_pages/"+file.split("/")[-2], "w", encoding="utf-8")
        outfile.write(markdown)

        print(str(i)+" / "+str(len(files)))
        i+=1


def fetch_html(orig_root):
    root = Path(orig_root)
    exts = {".html"}
    files = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    files = [orig_root+x for x in files]
    return files


files = fetch_html("../WebCrawler//")
converter(files)
