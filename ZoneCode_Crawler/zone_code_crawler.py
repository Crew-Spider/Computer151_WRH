import requests
from bs4 import BeautifulSoup
from db_operations.connection import get_connected_database
from db_operations.config import get_request_headers, level_to_level_name
import threading
import time


def save_provinces_to_db():
    base_url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/"
    html = requests.get(base_url + "/index.html", headers=get_request_headers())
    print(html.status_code)
    soup = BeautifulSoup(html.text.encode('iso-8859-1').decode('gbk'), features="lxml")
    results = soup.find("table", {"class": "provincetable"}).find_all("tr", {"class": "provincetr"})
    
    db = get_connected_database()
    threads = []
    for res in results:
        for prov in res.find_all("a"):
            if db["zonecode"].find({"name": prov.text}).count() != 0:
                continue
            # save_one_province_to_db(prov, db, base_url)
            thread = threading.Thread(
                target=save_one_province_to_db,
                args=(prov, db, base_url)
            )
            threads.append(thread)
            thread.start()
    for thread in threads:
        thread.join()



def save_one_province_to_db(prov, db, base_url):
    province = {
            "id": prov["href"].replace(".html", ""),
            "name": prov.text,
            "level": "1",
            "subs": [],
    }
    province["subs"] = get_subs(base_url, province["id"], 2)
    db["zonecode"].insert(
        province
    )
    print("A level 1 task finished!" + " " + province["name"])



def get_subs(base_url, pid, level):
    sub_type = level_to_level_name[level]
    again = False
    html = None
    try:
        html = requests.get(base_url + pid + ".html", headers=get_request_headers(), timeout=10)
    except:
        again = True

    while (again == True or html.status_code != 200):
        if again == True:
            again = False
            print("overtime!")
        else:
            print(html.status_code)
        try:
            html = requests.get(base_url + pid + ".html", headers=get_request_headers(), timeout=10)
        except:
            again = True
        time.sleep(3)
    try:
        soup = BeautifulSoup(html.text.encode('iso-8859-1').decode('gbk'), features="lxml")
    except:
        soup = BeautifulSoup(html.text.encode('iso-8859-1'), features="lxml")
        db = get_connected_database()
        db["error"].update_one({"id": "2333"}, {"$push": {"errors":{
            "pid": pid, "level": level, "base_url": base_url
        }}})
        db["error"].update_one({"id": "2333"}, {"$inc": {"error":1}})
    results = soup.find(
        "table", {"class": sub_type + "table"}
    )

    if results is None:
        level += 1
        sub_type = level_to_level_name[level]
        results = soup.find(
            "table", {"class": sub_type + "table"}
        )

    results = results.find_all(
        "tr", {"class": sub_type + "tr"}
    )

    current_subs = []

    for res in results:
        tmp = {}
        end = False
        additional_id_to_url = ""
        if level < 5:
            tmp2 = res.find_all("a")
            if tmp2 is not None and len(tmp2) != 0:
                res = tmp2
                additional_id_to_url = res[1]["href"].replace(".html", "").split("/")[-1]
                tmp["id"] = res[0].text
                tmp["name"] = res[1].text
            else:
                res = res.find_all("td")
                tmp["id"] = res[0].text
                tmp["name"] = res[1].text
                end = True
        else:
            res = res.find_all("td")
            tmp["id"] = res[0].text
            tmp["name"] = res[2].text
            end = True
            if tmp["name"] == "":
                tmp["name"] = "高康社区居委会"

        sub = {
            "id": tmp["id"],
            "name": tmp["name"],
            "level": level,
            "subs": [],
            "pid": pid,
        }
        if not end:
            sub["subs"] = get_subs(
                base_url + pid[-2:-1] + pid[-1] + "/",
                additional_id_to_url,
                level + 1
            )
            print("A level " + str(level) + " task finished!" + " " + sub["name"]) 
            # time.sleep(0.5)     
        current_subs.append(sub)

    return current_subs


def add_zeros(s):
    if len(s) < 12:
        s = s + "".zfill(12 - len(s));
    return s



# if __name__ == "__main__":
    # save_provinces_to_db()

    # res = requests.get("https://www.baidu.com")
    # print(res.status_code)
    
    # db = get_connected_database()
    # db["error"].update_one({"id": "2333"}, {"$push": {"errors":{"2333":"23"}}})
    # db["error"].update_one({"id": "2333"}, {"$pull": {"errors":{"pid":"420684103"}}})
    # db["error"].update_one({"id": "2333"}, {"$inc": {"error":-1}})

    # print(get_subs("http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/44/", 
    # "4419", 3))

    # db = get_connected_database()
    # db["zonecode"].drop()

    # db = get_connected_database()
    # a = db["zonecode"].find_one({"name": "四川省"})
    # for city in a["subs"]:
    #     for county in city["subs"]:
    #         for town in county["subs"]:
    #             for village in town["subs"]:
    #                 if village["name"] == "高康社区居委会":
    #                     print(town["subs"].index(village))
    #                     print(county["subs"].index(town))
    #                     print(city["subs"].index(county))
    #                     print(a["subs"].index(city))
    # print(a["subs"][4]["subs"][4]["subs"][12]["subs"][9]["name"])

    # db["zonecode"].remove({"name": a["name"]})
    # db["zonecode"].insert(a)

    # db = get_connected_database()
    # provs = db["zonecode"].find({})
    # for prov in provs:
    #     prov["id"] = add_zeros(prov["id"])
    #     for city in prov["subs"]:
    #         city["id"] = add_zeros(city["id"])
    #         city["pid"] = add_zeros(city["pid"])
    #         for county in city["subs"]:
    #             county["id"] = add_zeros(county["id"])
    #             county["pid"] = add_zeros(county["pid"])
    #             for town in county["subs"]:
    #                 town["id"] = add_zeros(town["id"])
    #                 town["pid"] = add_zeros(town["pid"])
    #                 for village in town["subs"]:
    #                     village["id"] = add_zeros(village["id"])
    #                     village["pid"] = add_zeros(village["pid"])
    #     db["zonecodes"].insert(prov)
    #     print("finish one")


