from html_to_markdown import convert
from bs4 import BeautifulSoup
import os
from pathlib import Path
import uuid

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in ["script", "style", "link"]:
        for t in soup.find_all(tag):
            t.decompose()

    for tag in soup.select("nav, header, footer, [role='navigation']"):
        tag.decompose()

    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.Comment))):
        comment.extract()

    for tag in soup.find_all():
        if not tag.get_text(strip=True) and tag.name not in ["br", "hr"]:
            tag.decompose()

    for tag in soup.find_all(True):
        if 'class' in tag.attrs:
            del tag.attrs['class']

    return str(soup)


def converter(response, uni):
    data = clean_html(response.body.decode("utf-8"))
    markdown = convert(data)

    if isinstance(markdown, bytes):
        markdown = markdown.decode("utf-8")

    print("\n\n\n\n Markdown Created \n\n\n\n")

    filename = f"{uuid.uuid4().hex}.txt"
    folder = Path("cleaned_pages") / uni
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    return str(file_path.resolve())

