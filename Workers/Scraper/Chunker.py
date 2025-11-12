from bs4 import BeautifulSoup
from transformers import AutoTokenizer
import os
from Cleaner import clean_html

# #The input and output files are declared
# in_file="test2.html"


def chunker(in_file):
    in_f = open(in_file,"r")
    html = clean_html(in_f)

    soup = BeautifulSoup(html, "html.parser")

    elements = []
    for elem in soup.find_all(recursive=True):
        elements.append(str(elem)) 

    print("No. of Elements : ",len(elements))

    chunk_size = 1024
    chunks = []
    current_chunk = []
    current_len = 0

    tokenizer = AutoTokenizer.from_pretrained("jinaai/reader-lm-1.5b")

    for elem in elements:
        tokens_len = len(tokenizer.encode(elem))
        if current_len + tokens_len > chunk_size:
            chunks.append("".join(current_chunk))
            current_chunk = [elem]
            current_len = tokens_len
        else:
            current_chunk.append(elem)
            current_len += tokens_len

    if current_chunk:
        chunks.append("".join(current_chunk))

    print("No. of Chunks : ",len(chunks))

    return chunks