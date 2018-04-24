import requests
from bs4 import BeautifulSoup

html = requests.get(
    r"http://news.baidu.com/ns?word=%E4%B8%8A%E6%B5%B7%E6%B5%B7%E4%BA%8B%E5%A4%A7%E5%AD%A6&pn=0&rn=20&cl=2")

soup = BeautifulSoup(html.text, features="lxml")
news = soup.find_all("div", {"class": "result"})

for new in news:
    time = new.find("p").get_text().split("\xa0")[-1]
    link_tag = new.find("a")
    title = link_tag.get_text()
    link = link_tag["href"]
    with open("result.txt", mode="a", encoding="utf-8") as f:
        f.write(title + "," + time + "," + link + "\n")

    