import json

f = open("final_data2.json", "r", encoding="utf-8")
data = json.load(f)

names = {}

for d in data:
    if d["uni"] not in names.keys():
        names[d["uni"]]=1
    else:
        names[d["uni"]]+=1

print(names)

#{'GCUF', 'IUB', 'NUML', 'BZU', 'USWAT', 'LSE', 'SU', 'SZABIST', 'Unknown', 'UOP'}

#['BZU', 'GCUF', 'IQRA', 'IUB', 'LSE', 'NUML', 'SU', 'SZABIST', 'UOP', 'USA', 'USINDH', 'USWAT', 'WUM']
#['BZU', 'GCUF', 'IOBM', 'IQRA', 'IUB', 'LSE', 'NUML', 'SU', 'SZABIST', 'UOP', 'USA', 'USINDH', 'USWAT', 'VU', 'WUM']

#['IOBM','VU']