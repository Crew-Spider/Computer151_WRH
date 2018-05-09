import requests
from bs4 import BeautifulSoup
import re
import json
import os

def save_questions(topic_id, save_file):
    url = "https://www.thebump.com/real-answers/v1/topics/{topic_id}/questions"
    url = url.format(topic_id=topic_id)
    params = {
        "include_user": "true",
        "page_num": 1,
        "page_size": 1
    }
    content = requests.get(url, params=params).json()
    params["page_size"] = content["total"]
    content = requests.get(url, params=params).json()
    with open(save_file, mode="a", encoding="utf-8") as f:
        for question in content["questions"]:
            f.write(question["title"] + "\n")


def mkdir(path):  
    folder = os.path.exists(path)  
    if not folder:
        os.makedirs(path)


def crawler_thebump():
    html = requests.get("https://www.thebump.com/real-answers/themes")
    soup = BeautifulSoup(html.text, features="lxml")

    # 获取变量'preloadThemes'
    pattern = re.compile(r"var preloadThemes = {.*};", re.MULTILINE | re.DOTALL)

    # 获取变量'preloadThemes'的值
    pattern2 = re.compile(r"{.*}", re.MULTILINE | re.DOTALL)

    script = soup.find("script", text=pattern)
    result = pattern2.search(pattern.search(script.text).group(0)).group(0)
    result = json.loads(result)

    '''
            文件按照如下结构存放:
                crawler_thebump/
                    theme1/
                        topic1/
                        topic2/
                        ...
                    theme2/
                        topic1/
                        topic2/
                        ...
                    ...    
            '''
    for theme in result["themes"]:
        theme_name = theme["name"]
        mkdir(theme_name)
        print ("getting theme=" + theme_name + "---------------------------------------------")
        for topic in theme["topics"]:
            topic_name = topic["name"]
            print ("getting topic=" + topic_name)
            save_questions(topic["id"], theme_name + "/" + topic_name + ".txt")

crawler_thebump()