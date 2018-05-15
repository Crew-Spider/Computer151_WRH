import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import pymongo


# 主程序
def crawler_thebump2():
    html = requests.get("https://www.thebump.com/real-answers/stages")
    soup = BeautifulSoup(html.text, features="lxml")

    # 用于获取变量'gon.stages'
    pattern = re.compile(r"gon.stages=\[.*\];", re.MULTILINE | re.DOTALL)

    # 用于获取变量'gon.stages'的值
    pattern2 = re.compile(r"\[.*\]", re.MULTILINE | re.DOTALL)

    script = soup.find("script", text=pattern)
    result = pattern2.search(pattern.search(script.text).group(0)).group(0)
    result = json.loads(result)
    
    for category in result:
        category_name = category["name"]
        
        # 只保存这两个category
        if category_name not in ["Pregnancy", "Parenting"]:
            continue
        
        print ("getting category=" + category_name + "---------------------------------------")

        for subcategory in category["children"]:
            subcategory_name = subcategory["name"]
            print ("getting subcategory=" + subcategory_name)

            ######################################################################
            # 修改这里，选择保存到CSV还是Mongo
            ######################################################################
            save_questions_to_csv(
                stage_id=subcategory["id"],
                category_name=category_name,
                subcategory_name=subcategory_name,
                page_size=500
            )
            # 注意：保存至Mongo时不查重
            # save_questions_to_mongo(
            #     stage_id=subcategory["id"],
            #     category_name=category_name,
            #     subcategory_name=subcategory_name,
            #     page_size=500,
            #     mongo_host="localhost",
            #     port=27017,
            #     database_name="local",
            #     collection_name="thebump_questions"
            # )



# 保存至CSV文件
def save_questions_to_csv(stage_id, category_name, subcategory_name, page_size=30):
    url = "https://www.thebump.com/real-answers/v1/categories/{stage_id}/questions?filter=ranking"
    url = url.format(stage_id=stage_id)
    params = {
        "page_num": 1,
        "page_size": page_size,
    }

    # 第一遍可以得到total的值
    content = requests.get(url, params=params).json()
    total = content["total"]

    # 这相当于一个do-while
    # 一次循环保存page_size条问题
    while True:
        data = {
            "title": [],
            "created_at": [],
            "user_id": [],
            "username": [],
            "category_name": [],
            "subcategory_name": [],
        }
        for question in content["questions"]:
            data["title"].append(question["title"].replace("\n", " "))
            data["created_at"].append(question["created_at"])
            data["user_id"].append(question["user_id"])
            data["username"].append(question["user"]["username"])
            data["category_name"].append(category_name)
            data["subcategory_name"].append(subcategory_name)

        columns = [
            "title", "created_at", "user_id",
            "username", "category_name", "subcategory_name"
        ]

        with open("data.csv", "a") as f:
            pd.DataFrame(data, columns=columns).to_csv(f, header=False, index=False)
        
        total -= page_size
        if (total > 0):
            params["page_num"] += 1
            content = requests.get(url, params=params).json()
        else:
            break


# 保存至Mongo数据库(无查重功能)
def save_questions_to_mongo(stage_id, category_name, 
        subcategory_name, page_size=30,
        mongo_host="localhost", port=27017,
        database_name="local", collection_name="thebump_questions"):

    client = pymongo.MongoClient(host=mongo_host, port=port)
    db = client[database_name]
    collection = db[collection_name]

    url = "https://www.thebump.com/real-answers/v1/categories/{stage_id}/questions?filter=ranking"
    url = url.format(stage_id=stage_id)
    params = {
        "page_num": 1,
        "page_size": page_size,
    }

    # 第一遍可以得到total的值
    content = requests.get(url, params=params).json()
    total = content["total"]

    # 这相当于一个do-while
    # 一次循环保存page_size条问题
    while True:
        datas = []
        for question in content["questions"]:
            data = {}
            data["title"] = question["title"].replace("\n", " ")
            data["created_at"] = question["created_at"]
            data["user_id"] = question["user_id"]
            data["username"] = question["user"]["username"]
            data["category_name"] = category_name
            data["subcategory_name"] = subcategory_name
            datas.append(data)

        collection.insert_many(datas)

        total -= page_size
        if (total > 0):
            params["page_num"] += 1
            content = requests.get(url, params=params).json()
        else:
            break
    
    


if __name__ == "__main__":
    crawler_thebump2()
