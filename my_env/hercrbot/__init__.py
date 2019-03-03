import telebot
import hashlib
import datetime
import requests
import json
import time
import random
import re

token = "651338302:AAEebdAeOJ7STL0iBjpELGy5FVJjpfvO4B0"
bot = telebot.TeleBot(token)
admin_id = 444585041


def add_months(sourcedate=datetime.datetime.now(), days=30):
    return (sourcedate + datetime.timedelta(days=days)).date()


def allow(m):
    cid = m.from_user.id
    to_check = m.text
    to_write = []
    valid = False
    time_days = 0
    with open("keys.txt", "r") as file:
        for line in file.readlines():
            if len(line.split()) == 3 and line.split()[1] == to_check:
                bot.send_message(cid, "Доступ предоставлен!")
                time_days = int(line.split()[2])
                valid = True
            else:
                to_write.append(line)
    with open("keys.txt", "w") as file:
        if len(to_write) == 0:
            to_write = [""]
        file.write("".join(to_write))
    if not valid:
        bot.send_message(cid, "Код неверный")
    else:
        with open("users.txt", "r+") as file:
            count = len(file.readlines())
            until = add_months(days=time_days)
            file.write("{} Id: {}, until: {}\n".format(count, cid, until))


@bot.message_handler(commands=["g_key"])
def main(m):
    cid = m.from_user.id
    if cid == admin_id:
        if len(m.text.split()) == 2:
            time_days = int(m.text.split()[1])
        else:
            time_days = 30
        string = str(datetime.datetime.now()) + "1"
        code = hashlib.md5(str(string).encode()).hexdigest()
        bot.send_message(cid, "{}".format(code))
        with open("keys.txt", "a") as file:
            file.write("key: {} {}\n".format(code, time_days))


@bot.message_handler(commands=["start"])
def main(m):
    cid = m.from_user.id
    ms = bot.send_message(cid, "Пришлите мне код.")
    bot.register_next_step_handler(ms, allow)


@bot.message_handler(commands=["send_to_all"])
def main(m):
    cid = m.from_user.id
    users = {}
    if cid == admin_id and len(m.text.split()) > 2:
        with open("users.txt", "r") as file:
            for line in file.readlines():
                print(line)
                user = re.search("Id: (\d{6,12})", line)
                until_date = re.search("until: (\d\d\d\d-\d\d-\d\d)", line)
                if user and datetime.datetime.today() < datetime.datetime.strptime(until_date.group(1), '%Y-%m-%d'):
                    u_id = re.search("^(\d{1,10}) Id:", line).group(1)
                    users[u_id] = user.group(1)
        string = " ".join(m.text.split()[1:])
        try:
          old_link = re.search("(?P<url>https?://[^\s]+)", string).group("url")
          if 'tradingview.com' in old_link:
            for us, user_id in users.items():
             req = requests.post("https://api.rebrandly.com/v1/links",
             data = json.dumps({
             "destination": "{}".format(old_link)
              , "domain": { "fullName": "tradingview.com.ru" }
             , "slashtag": "symbols_BTC_USD{}_{}_{}".format(random.randint(100,999), us, random.randint(100,999))
             , "title": "{}?{}".format(old_link, us)
             }),
             headers={
             "Content-type": "application/json",
             "apikey": "9ad741739d13409f8b5c1505d03d53f1"
              })
             if (req.status_code == requests.codes.ok):
              link = req.json()
              string = string.replace(old_link, link['shortUrl'])
              bot.send_message(user_id, string)
             else:
              print(req.json())
          else:
            for us, user_id in users.items():
              bot.send_message(user_id, string)
        except Exception:
          for us, user_id in users.items():
            bot.send_message(user_id, string)


while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print("Error################\n", e)
        bot.stop_polling()
        time.sleep(10)