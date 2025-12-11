import requests
from bs4 import BeautifulSoup, Comment
import re


url = "https://www.harvard.edu/"
resp = requests.get(url, timeout=10)
resp.raise_for_status()            
html = resp.text       

soup = BeautifulSoup(html, "html.parser")

full_html = soup.prettify()


def clean_html_keep_structure(html_text):
    soup = BeautifulSoup(html_text, "html.parser")

    # 1) Handle lazy-loaded images: prefer data-src/data-lazy before src
    for img in soup.find_all("img"):
        if not img.get("src"):
            # common lazy attributes
            for lazy_attr in ("data-src", "data-original", "data-lazy", "data-srcset"):
                if img.get(lazy_attr):
                    img["src"] = img[lazy_attr]
                    break

    # 2) Remove truly useless tags (scripts, styles, trackers, external embeds)
    for tag_name in ["script", "style", "link", "iframe", "embed", "object", "applet", "canvas", "svg"]:
        for t in soup.find_all(tag_name):
            # allow keeping link tags that are not styles (rare) — but drop stylesheets
            if tag_name == "link":
                rel = (t.get("rel") or [])
                if "stylesheet" in rel:
                    t.decompose()
                else:
                    t.decompose()
            else:
                t.decompose()

    # 3) Remove comments
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    # 4) noscript: sometimes contains fallback content (text/html). If it's short and clearly human text, keep it; else drop.
    for nos in soup.find_all("noscript"):
        text = (nos.get_text(" ", strip=True) or "").strip()
        # heuristic: if it contains common tags or long html, try to preserve inner text; otherwise remove
        if len(text) > 50 and "<" not in text:
            # replace noscript with its inner text wrapped in a <div>
            new = soup.new_tag("div")
            new.string = text
            nos.replace_with(new)
        else:
            nos.decompose()

    # 5) Allowed tags to keep and preserve structure (others not listed will be unwrapped)
    allowed = {
        "p", "br", "hr",
        "h1","h2","h3","h4","h5","h6",
        "ul","ol","li",
        "a","img",
        "strong","b","em","i","u","small","sub","sup",
        "blockquote","pre","code",
        "table","thead","tbody","tr","td","th","caption",
        "section","article","main","header","footer","nav","aside",
        "div","span"
    }

    # 6) Clean attributes: keep href, src, alt, title; remove style/class/id/on* and data-/aria-*
    keep_attrs = {"href", "src", "alt", "title", "cite"}
    for tag in soup.find_all(True):
        if tag.name not in allowed:
            # unwrap: remove tag but keep children (preserves inner content)
            tag.unwrap()
            continue

        # prune attributes
        attrs = dict(tag.attrs)
        for k in list(attrs.keys()):
            if k in keep_attrs:
                # keep as-is
                continue
            # for img keep src/srcset handling: allow srcset if you want
            if tag.name == "img" and k in ("srcset", "data-srcset"):
                continue
            # remove event handlers, data-*, aria-*, style, class, id
            if k.startswith("on") or k.startswith("data-") or k.startswith("aria-") or k in ("style", "class", "id", "role"):
                del tag.attrs[k]
            else:
                # remove any other non-essential attribute
                del tag.attrs[k]

    # 7) Optional: remove empty tags that contain no text nor useful child (helps reduce nav noise)
    def is_empty_tag(t):
        # consider img non-empty if it has src
        if t.name == "img":
            return not (t.get("src"))
        # whitespace-only or no children
        txt = t.get_text("", strip=True)
        if txt:
            return False
        # if it has any meaningful child tags (like table rows), keep
        for child in t.find_all(True):
            if child.name in ("img", "a", "table", "pre", "code", "li", "p", "h1","h2","h3"):
                return False
        return True

    for t in list(soup.find_all()):
        if is_empty_tag(t):
            t.decompose()

    # 8) Final: return cleaned HTML (pretty if you want)
    cleaned_html = str(soup)
    return cleaned_html

# usage
html = full_html
cleaned = clean_html_keep_structure(html)
with open("Crawled.html", "w", encoding="utf-8") as f:
    f.write(cleaned)