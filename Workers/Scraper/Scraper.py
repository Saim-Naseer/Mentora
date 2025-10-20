import requests

url = "https://www.harvard.edu/"

response = requests.get(url)

with open("harvard_homepage.html", "w", encoding="utf-8") as file:
    file.write(response.text)