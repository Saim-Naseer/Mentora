from build_prompt import build_prompt
from transformers import AutoTokenizer
import json

f = open("pdf_urls.json","r",encoding="utf-8")
data = json.load(f)

# f2 = open("data.json","r",encoding="utf-8")
# prev = json.load(f2)

tokenizer = AutoTokenizer.from_pretrained("./tokenizer")

def estimate_tokens(text):
    return len(tokenizer.encode(text))

print(estimate_tokens(str(data)))

# new_list = []
# for d in data:
#     tokens = estimate_tokens(str(d))
#     if tokens>15000:
#         pieces=(tokens//15000)+1
#         length = len(d["text"])
#         piece_length = length//pieces
#         gap = piece_length//4
#         for i in range(pieces):
#             if i==0:
#                 link = d["link"]
#                 uni = d["uni"]
#                 text = d["text"][0:piece_length]
#                 new_list.append({"link":link,"uni":uni,"text":text})
#             else:
#                 link = d["link"]
#                 uni = d["uni"]
#                 text = d["text"][(i*piece_length)-gap:(i+1)*piece_length]
#                 new_list.append({"link":link,"uni":uni,"text":text})
#     else:
#         new_list.append(d)

# i=0
# for d in new_list:
#     print(i," : ",estimate_tokens(str(d)))
#     i+=1

