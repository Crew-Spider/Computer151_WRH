
level_to_level_name = {
    1: "province",
    2: "city",
    3: "county",
    4: "town",
    5: "village"
}


def get_database_dict_info():

    db = {
        "host": "127.0.0.1",
        "port": 27017,
        "user": "",
        "database": "ZoneCode",
        "password": "",
    }

    return db


def get_request_headers():
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    return {'User-Agent': user_agent}