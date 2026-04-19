import json
file = open('final_data3.json', 'r', encoding="utf-8") 
data = json.load(file)

for d in data:
    print(d["object"]["university"]["name"]["val"])