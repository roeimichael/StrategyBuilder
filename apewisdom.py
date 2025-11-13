from bs4 import BeautifulSoup
import requests
import re
import urllib.request


def getdata(url):
    r = requests.get(url)
    return r.text


for i in range(1, 4750):
    htmldata = getdata(f"http://justinmaller.com/wallpaper/{i}/")
    soup = BeautifulSoup(htmldata, 'html.parser')
    for item in soup.find_all('img'):
        if len(item['src']) >= 70:
            urllib.request.urlretrieve(item['src'], f'./wallpaper/wp-{i}.jpg')
            print(item['src'])