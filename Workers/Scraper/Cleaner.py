from bs4 import BeautifulSoup
import os
#The input and output files are declared
in_file="test.html"
out_file="test2.html"

#The previous output file is removed
if os.path.exists(out_file):
    os.remove(out_file)

in_file=open(in_file, "r")
out_file=open(out_file,"w")

def clean_html(f):
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    for tag in ["script", "style"]:
        for t in soup.find_all(tag):
            t.decompose()
    return str(soup)

out_file.write(clean_html(in_file))