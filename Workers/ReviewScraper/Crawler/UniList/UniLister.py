import requests
import json

offset=0
url_list=[]
for i in range(22):
    url = "https://www.eduopinions.com/wp-admin/admin-ajax.php?action=load_featured_popular&id=1337&type=country&offset="
    response = requests.get(url+str(offset))
    if response.status_code == 200:
        data = response.json()
        for d in data.get("data", []):
            url_list.append(d.get("uni_url"))
    else:
        print("error")
    offset+=5

with open("urls.json", "w") as f:
    json.dump(url_list, f, indent=2)