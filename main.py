from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

nowtime = datetime.utcnow() + timedelta(hours=8)  # 东八区时间
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d") #今天的日期
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_ids = os.environ["USER_ID"]
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  if city is None:
    print('请设置城市')
    return None
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  if res is None:
    return None
  weather = res['data']['list'][0]
  return weather

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday_left():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def format_temperature(temperature):
  return math.floor(temperature)

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


try:
  client = WeChatClient(app_id, app_secret)
except WeChatClientException as e:
  print('微信获取 token 失败，请检查 APP_ID 和 APP_SECRET，或当日调用量是否已达到微信限制。')
  exit(502)

wm = WeChatMessage(client)
weather = get_weather()
if weather is None:
  print('获取天气失败')
  exit(422)
data = {
  "city": {
    "value": city,
    "color": get_random_color()
  },
  "date": {
    "value": today.strftime('%Y年%m月%d日'),
    "color": get_random_color()
  },
  "weather": {
    "value": weather['weather'],
    "color": get_random_color()
  },
  "temperature": {
    "value": math.floor(weather['temp']),
    "color": get_random_color()
  },
  "highest": {
    "value": math.floor(weather['high']),
    "color": get_random_color()
  },
  "lowest": {
    "value": math.floor(weather['low']),
    "color": get_random_color()
  },
  "love_days": {
    "value": get_count(),
    "color": get_random_color()
  },
  "birthday_left": {
    "value": get_birthday_left(),
    "color": get_random_color()
  },
  "words": {
    "value": get_words(),
    "color": get_random_color()
  },
}

count = 0
try:
  for user_id in user_ids:
    res = wm.send_template(user_id, template_id, data)
    count+=1
except WeChatClientException as e:
  print('微信端返回错误：%s。错误代码：%d' % (e.errmsg, e.errcode))
  exit(502)

print("发送了" + str(count) + "条消息")
