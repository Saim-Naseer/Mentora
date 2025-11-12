from bs4 import BeautifulSoup
import os, re
from transformers import AutoTokenizer

# #The input and output files are declared
# in_file="harvard_homepage.html"
# out_file="test2.html"

# #The previous output file is removed
# if os.path.exists(out_file):
#     os.remove(out_file)

# in_file=open(in_file, "r")
# out_file=open(out_file,"w")

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

    for tag in soup.find_all(string=True):
        tag.replace_with(re.sub(r"\s+", " ", tag))
    return str(soup)

def get_token_count(file):
    checkpoint = "jinaai/reader-lm-1.5b"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    f = open(file, "r")
    data = f.read()
    return tokenizer.encode(data)

# out_file.write(clean_html(in_file))
if __name__ == "__main__":
    in_f = "harvard_homepage.html"
    out_f = "test6.html"
    in_file = open(in_f, "r")
    if os.path.exists(out_f):
        os.remove(out_f)
    out_file = open(out_f, "w")

    out_file.write(clean_html(in_file))

    print("Before : ",len(get_token_count(in_f)),"    After  : ",len(get_token_count(out_f)))