from bs4 import BeautifulSoup
from transformers import AutoTokenizer
import os
from Cleaner import clean_html

# #The input and output files are declared
# in_file="test2.html"
def get_leaf_elements(soup):

    leaves = []

    def recurse(node):
        # Only consider Tag objects, ignore NavigableStrings at this point
        from bs4 import Tag

        if isinstance(node, Tag):
            children = [c for c in node.children if isinstance(c, Tag)]
            if not children:
                # Node has no child tags → it's a leaf
                leaves.append(str(node))
            else:
                # Recurse into children
                for c in children:
                    recurse(c)

    recurse(soup)
    return leaves


def chunker(in_file):
    in_f = open(in_file,"r")
    html = clean_html(in_f)

    soup = BeautifulSoup(html, "html.parser")

    # elements = []
    # for elem in soup.find_all(recursive=True):
    #     elements.append(str(elem)) 

    elements = get_leaf_elements(soup)

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

    n_e=0
    tot_e=0
    excess_e=[]
    for e in elements:
        n_e+=1
        s = len(tokenizer.encode(e))
        tot_e+=s
        if s>1024:
            excess_e.append((s,n_e))

    print("Average Element Size : ",tot_e/len(elements))

    for e in excess_e:
        print(e)

    n_c=0
    tot=0
    excess=[]
    for c in chunks:
        n_c+=1
        s = len(tokenizer.encode(c))
        tot+=s
        if s>1024:
            excess.append((s,n_c))

    print("Average Chunk Size : ",tot/len(chunks))

    for e in excess:
        print(e)


    return chunks

# if __name__ == "__main__":
#     chunks = chunker("harvard_homepage.html")

#     f = open("test9.html","w")
#     n=0
#     for c in chunks:
#         n+=1
#         f.write("\n--------------------------------- Chunk # "+str(n)+"--------------------------------- \n")
#         f.write(c)
