# -*- coding: UTF-8 -*-
import json
import random
from time import time, localtime
import requests
import cityinfo
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    return f"#{random.randint(0, 0xFFFFFF):06x}"


def get_access_token():
    app_id = config["app_id"]
    app_secret = config["app_secret"]
    post_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    try:
        return get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)


def get_weather(province, city):
    try:
        city_id = cityinfo.cityInfo[province][city]["AREAID"]
    except KeyError:
        print("推送消息失败，请检查省份或城市是否正确")
        os.system("pause")
        sys.exit(1)

    headers = {
        "Referer": f"http://www.weather.com.cn/weather1d/{city_id}.shtml",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    url = f"http://d1.weather.com.cn/dingzhi/{city_id}.html?_={int(round(time() * 1000))}"
    response = get(url, headers=headers)
    response.encoding = "utf-8"
    weatherinfo = eval(response.text.split(";")[0].split("=")[-1])["weatherinfo"]
    return weatherinfo["weather"], weatherinfo["temp"], weatherinfo["tempn"], weatherinfo["wd"], weatherinfo["ws"]


def get_birthday(birthday, year, today):
    is_lunar = birthday.startswith("r")
    r_month, r_day = (int(birthday.split("-")[1]), int(birthday.split("-")[2])) if is_lunar else (0, 0)
    birthday_date = ZhDate(year, r_month, r_day).to_datetime().date() if is_lunar else date(year, int(birthday.split("-")[1]), int(birthday.split("-")[2]))

    if today > birthday_date:
        birthday_date = ZhDate(year + 1, r_month, r_day).to_datetime().date() if is_lunar else date(year + 1, int(birthday.split("-")[1]), int(birthday.split("-")[2]))

    return (birthday_date - today).days


def get_ciba():
    url = "https://open.iciba.com/dsapi/"
    response = requests.get(url, headers={'Content-Type': 'application/json', 'User-Agent': "Mozilla/5.0"})
    data = response.json()
    note_en = data["content"][:20]
    note_ch = data["note"][:20]
    return note_ch, note_ch[20:], note_en, note_en[20:]


def send_message(to_user, access_token, city_name, weather, max_temperature, min_temperature, note_ch, note_ch2,
                 note_en, note_en2, love, loveT, loveTT, loveTTT, loveTTTT, wd, ws, one, days, goodMonring):
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    today = datetime.now()
    week = week_list[today.isoweekday() % 7]
    love_date = date(*map(int, config["love_date"].split("-")))
    love_days = (today.date() - love_date).days

    birthdays = {k: v for k, v in config.items() if k.startswith("birth")}
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {"value": f"{today.date()} {week}", "color": get_color()},
            "city": {"value": city_name, "color": get_color()},
            "weather": {"value": weather, "color": get_color()},
            "min_temperature": {"value": min_temperature, "color": get_color()},
            "max_temperature": {"value": max_temperature, "color": get_color()},
            "love_day": {"value": love_days, "color": get_color()},
            "note_en": {"value": note_en, "color": get_color()},
            "note_en2": {"value": note_en2, "color": get_color()},
            "note_ch": {"value": note_ch, "color": get_color()},
            "note_ch2": {"value": note_ch2, "color": get_color()},
            "love": {"value": love, "color": get_color()},
            "loveT": {"value": loveT, "color": get_color()},
            "loveTT": {"value": loveTT, "color": get_color()},
            "loveTTT": {"value": loveTTT, "color": get_color()},
            "loveTTTT": {"value": loveTTTT, "color": get_color()},
            "wd": {"value": wd, "color": get_color()},
            "ws": {"value": ws, "color": get_color()},
            "day": {"value": days, "color": get_color()},
            "one": {"value": one, "color": get_color()},
            "goodMonring": {"value": goodMonring, "color": get_color()},
        }
    }

    for k, v in birthdays.items():
        birth_day = get_birthday(v["birthday"], today.year, today.date())
        birthday_data = f"今天{v['name']}生日哦，祝{v['name']}生日快乐！" if birth_day == 0 else f"距离{v['name']}的生日还有{birth_day}天"
        data["data"][k] = {"value": birthday_data, "color": get_color()}

    response = post(url, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=data).json()
    if response["errcode"] in {40037, 40036, 40003}:
        print("推送消息失败，请检查模板id或微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)


def get_random_data_from_json_files():
    files = [f for f in os.listdir('.') if f.endswith('.json')]
    if not files:
        return "No json files found in the directory."

    with open(random.choice(files), 'r', encoding='utf-8') as f:
        data = json.load(f)

    random_index = random.randint(1, len(data))
    return data[str(random_index)] + "  to 周舒萍"


def getDay():
    return (datetime.now() - datetime(2024, 10, 3)).days

def getOneDay():
    return (datetime.now() - datetime(2024, 11, 23)).days

def getLenLove(loves):
    love_parts = [loves[i:i + 20] for i in range(0, min(len(loves), 100), 20)]
    return (*love_parts, *[""] * (5 - len(love_parts)))  # Fill with empty strings if less than 5 parts


if __name__ == "__main__":
    try:
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except (FileNotFoundError, SyntaxError) as e:
        print(f"推送消息失败，请检查config.txt文件是否与程序位于同一路径: {e}")
        os.system("pause")
        sys.exit(1)

    accessToken = get_access_token()
    users = config["user"]
    province, city = config["province"], config["city"]
    weather, max_temperature, min_temperature, wd, ws = get_weather(province, city)
    note_ch, note_ch2, note_en, note_en2 = get_ciba()
    loves = get_random_data_from_json_files()

    love, loveT, loveTT, loveTTT, loveTTTT = getLenLove(loves)
    one = getOneDay()
    day = getDay()
    goodMonring = "早安，希望你今天开开心心。"
    for user in users:
        send_message(user, accessToken, city, weather, max_temperature, min_temperature, note_ch, note_ch2, note_en,
                     note_en2, love, loveT, loveTT, loveTTT, loveTTTT, wd, ws, one, day, goodMonring)
    os.system("pause")
