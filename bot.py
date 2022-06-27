import pymysql
import datetime
import random
import telebot
import time
import traceback
import requests
from telebot import types
from bs4 import BeautifulSoup
bot = telebot.TeleBot("2100982880:AAF2_wJXYjKngBWvKFU-J65yAbR6hrSwIHc")


def timee():
    global now, cur_date, cur_time
    now = datetime.datetime.now()
    cur_date = now.strftime("%Y-%m-%d")
    cur_time = now.strftime("%H:%M:%S")
    return now, cur_date, cur_time


now, cur_date, cur_time = timee()


def MySQL(m, res=False):
    try:
        timee()
        global con, user
        user = m.chat.id
        con = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='kaneka',
            cursorclass=pymysql.cursors.DictCursor
        )
        with con.cursor() as cur:
            cur.execute("INSERT INTO `history`(user, date, time, message) VALUES(?, '?', '?', '?');",
                        (user, cur_date, cur_time, m.text))
            con.commit()
    except Exception as err:
        timee()
        print("MySQL | Ошибка подключения или ввода данных.",
            cur_date, cur_time, '\nError:', traceback.format_exc())


def main():
    @bot.message_handler(commands=['start'])
    def welcome(m, res=False):
        MySQL(m)
        bot.reply_to(
            m, "Привет! Меня зовут Канека!\n/menu - вызовет меню бота.")

    @bot.message_handler(commands=['menu'])
    def menu(m, res=False):
        MySQL(m)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = ["📓 История 🖊", "⌚️ Бэкапы 🕓"]
        button2 = ["📷 Факты 🖼", "♂ Gachi ♂"]
        button3 = ['📈 Курс валют 💲', '🪙 Орел и решка ❓']
        button4 = ['⛑ Коронавирус 💉', '💧 Погода ⛅']
        button5 = "💸 Пожертвовать 🙏"
        button6 = "📣 Обратная связь 🆘"
        markup.add(*button1)
        markup.add(*button2)
        markup.add(*button3)
        markup.add(*button4)
        markup.add(button5)
        markup.add(button6)
        bot.send_message(m.chat.id, 'Выберите пункт', reply_markup=markup)

    @bot.message_handler(content_types='text')
    def text(m, res=False):
        MySQL(m)
        if m.text == '⌚️ Бэкапы 🕓':
            bot.send_message(
                m.chat.id, 'Извините, но эта функция пока недоступна.')
        elif m.text == '💧 Погода ⛅':
            try:
                with con.cursor as cur:
                    cur.execute("SELECT * FROM `we_city`")
                    rows = cur.fetchall()
                    for row in rows:
                        if row['userid'] == user:
                            city = row['city']
                            print_insert_city = False
                    print_insert_city = True
                    if print_insert_city:
                        bot.send_message(m.chat.id, 'Введите ваш город.')
                        # Здесь программа должна ждать ввода пользователя
                        with con.cursor as cur:
                            cur.execute(
                                "INSERT INTO `we_city`(userid, city) VALUES('?', ?);", (user, m.text))
                            con.commit()
                            city = m.text
                r = requests.get(
                    f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=14020d00660f0fc786643a69daa39fab&units=metric')
                data = r.json()
                city = data["name"]
                cur_weather = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                pressure = data["main"]["pressure"]
                wind = data["wind"]["speed"]
                bot.send_message(m.chat.id, f"Погода в городе {city}.\n"
                                f"Температура: {cur_weather}\nВлажность: {humidity}\n"
                                f"Давление: {pressure} мм. рт. ст.\nСкорость ветра: {wind} м/c")
            except Exception as err:
                timee()
                print('Погода | Ошибка...', cur_date, cur_time,
                    '\nError:', traceback.format_exc())
                bot.send_message(
                    m.chat.id, 'Похоже, вы не так ввели город.\nЧто бы изменить город обратитесь к разработчику.')
        elif m.text == '⛑ Коронавирус 💉':
            try:
                bot.send_message(m.chat.id, "Информация загружается...")
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0"}
                url = 'https://стопкоронавирус.рф'
                source = requests.get(url, headers=headers)
                text = BeautifulSoup(source.content, 'html.parser')
                div = text.findAll(
                    "div", {'class': 'cv-countdown__item-value _accent'})
                div_h = text.find(
                    "div", {"class": "cv-countdown__item-value _accent-green"})
                timee()
                bot.send_message(m.chat.id, "Данные на " + cur_date + " " + cur_time + "\n😓 Госпитализировно: " +
                                div[0].text + "\n🤒 Выявлено: " + div[1].text + "\n😃 Выздоравлено: " + div_h.text)
            except Exception:
                timee()
                print("Курс валют | Ошибка вывода курса.", cur_date,
                    cur_time, '\nError:', traceback.format_exc())
                bot.send_message(
                    m.chat.id, 'Извините, ошибка вывода информации.')
        elif m.text == '📓 История 🖊':
            try:
                with con.cursor() as cur:
                    cur.execute(
                        "SELECT * FROM `history` ORDER BY `id` DESC LIMIT 10;")
                    rows = cur.fetchall()
                    for row in rows:
                        bot.send_message(m.chat.id, "ID: " + str(row['id']) + "\nUserID: " + str(row['user']) + "\nDate: " + str(
                            row['date']) + "\nTime: " + str(row['time']) + "\nMess: " + str(row['message']))
            except Exception as err:
                timee()
                print('История | Ошибка вывода', cur_date,
                    cur_time, '\nError:', traceback.format_exc())
                bot.send_message(m.chat.id, 'Извините, ошибка вывода истории.')
        elif m.text == '💸 Пожертвовать 🙏':
            bot.send_message(
                m.chat.id, 'Вы можете пожертвовать любую сумму на эти счета:\n\nСбербанк: 5469 4900 1720 4120\nТинькофф: 5536 9141 5526 5162\n\nМы очень благодарны вам!')
        elif m.text == '📣 Обратная связь 🆘':
            bot.send_message(
                m.chat.id, 'Здравствуйте! Канека создана начинающим разработчиком P1X∆RT при поддержке ParaNoid.\nНаписать разработчику: https://t.me/Pixartus')
        elif m.text == '📷 Факты 🖼':
            img_list = ['https://i.ucrazy.ru/files/pics/2017.02/interfakkt15.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt12.jpg', 
			'https://i.ucrazy.ru/files/pics/2017.02/interfakkt3.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt2.jpg', 
			'https://i.ucrazy.ru/files/pics/2017.02/interfakkt4.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt5.jpg', 
			'https://i.ucrazy.ru/files/pics/2017.02/interfakkt6.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt7.jpg', 
                        'https://i.ucrazy.ru/files/pics/2017.02/interfakkt8.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt9.jpg', 
						'https://i.ucrazy.ru/files/pics/2017.02/interfakkt10.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt11.jpg', 
						'https://i.ucrazy.ru/files/pics/2017.02/interfakkt13.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt14.jpg', 
						'https://i.ucrazy.ru/files/pics/2017.02/interfakkt16.jpg', 'https://i.ucrazy.ru/files/pics/2017.02/interfakkt17.jpg']
            bot.send_photo(m.chat.id, random.choice(img_list))
        elif m.text == '♂ Gachi ♂':
            gachi_list = ['/home/pixart/Kaneka/video/v1.mp4', '/home/pixart/Kaneka/video/v2.mp4', '/home/pixart/Kaneka/video/v3.mp4',
                        '/home/pixart/Kaneka/video/v4.mp4', '/home/pixart/Kaneka/video/v5.mp4', '/home/pixart/Kaneka/video/v6.mp4']
            bot.send_video(m.chat.id, open(random.choice(gachi_list), 'rb'))
        elif m.text == '📈 Курс валют 💲':
            try:
                bot.send_message(m.chat.id, 'Курс валют загружается...')
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0"}
                url_d = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80%D0%B0&client=ubuntu&hs=CIp&channel=fs&ei=RIMwYunON4uprgT9xJHACw&ved=0ahUKEwjpgIn4i8j2AhWLlIsKHX1iBLgQ4dUDCA0&uact=5&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80%D0%B0&gs_lcp=Cgdnd3Mtd2l6EAMyDwgAELEDEIMBEEMQRhCCAjILCAAQgAQQsQMQgwEyCggAELEDEIMBEEMyCwgAEIAEELEDEIMBMgoIABCxAxCDARBDMgQIABBDMgoIABCxAxCDARBDMgsIABCABBCxAxCDATILCAAQgAQQsQMQgwEyBAgAEEM6CggAEEcQsAMQyQM6BwgAEEcQsAM6CAgAELEDEIMBOgUIABCABDoHCAAQgAQQCkoECEEYAEoECEYYAFC6BVitG2CfHWgDcAF4AYABvAKIAfwPkgEIMC4xMy4wLjGYAQCgAQGwAQDIAQjAAQE&sclient=gws-wiz'
                url_e = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%95%D0%B2%D1%80%D0%BE&client=ubuntu&hs=zx9&channel=fs&ei=YoMwYv-ICvGnrgT23IPICw&ved=0ahUKEwj_wYKGjMj2AhXxk4sKHXbuALkQ4dUDCA0&uact=5&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%95%D0%B2%D1%80%D0%BE&gs_lcp=Cgdnd3Mtd2l6EAMyEAgAEIAEELEDEIMBEEYQggIyCAgAELEDEIMBMgsIABCABBCxAxCDATILCAAQgAQQsQMQgwEyCwgAEIAEELEDEIMBMgsIABCABBCxAxCDATILCAAQgAQQsQMQgwEyCwgAEIAEELEDEIMBMg4IABCABBCxAxCDARDJAzILCAAQgAQQsQMQgwE6BwgAEEcQsAM6CggAEEcQsAMQyQM6BwgAELADEEM6EgguEMcBENEDEMgDELADEEMYAToSCC4QxwEQowIQyAMQsAMQQxgBSgQIQRgASgQIRhgAUOcMWO4RYKIUaAFwAXgAgAF_iAHQA5IBAzAuNJgBAKABAcgBC8ABAdoBBAgBGAg&sclient=gws-wiz'
                url_b = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B1%D0%B8%D1%82%D0%BA%D0%BE%D0%B8%D0%BD%D0%B0&client=ubuntu&hs=2Jp&channel=fs&ei=toMwYrPHGeOkrgSUm6LICw&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B1%D0%B8%D1%82%D0%BA&gs_lcp=Cgdnd3Mtd2l6EAEYADIQCAAQgAQQsQMQgwEQRhCCAjIFCAAQgAQyBQgAEIAEMggIABCABBCxAzIICAAQgAQQsQMyBQgAEIAEMgUIABCABDIICAAQgAQQyQMyBQgAEIAEMgUIABCABDoHCAAQRxCwAzoKCAAQRxCwAxDJAzoLCAAQgAQQsQMQgwE6BwgAEIAEEAo6CggAELEDEIMBEEM6CAgAELEDEIMBSgQIQRgASgQIRhgAULoJWOAXYLwhaAJwAXgAgAHMAYgB5QaSAQUwLjYuMZgBAKABAcgBCMABAQ&sclient=gws-wiz'
                url_g = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D1%8B&client=ubuntu&hs=JfU&channel=fs&ei=2oMwYvmtEfeTwPAPlYqOyAs&ved=0ahUKEwj5gqa_jMj2AhX3CRAIHRWFA7kQ4dUDCA0&uact=5&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D1%8B&gs_lcp=Cgdnd3Mtd2l6EAMyDQgAEIAEELEDEEYQggIyCwgAEIAEELEDEIMBMggIABCABBCxAzIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQ6BwgAEEcQsAM6BwgAELADEEM6CAgAELEDEIMBOgkIABCABBAKECo6BwgAEIAEEAo6BggAEBYQHjoICAAQFhAKEB46BAgAEENKBAhBGABKBAhGGABQggVYyBtg_R5oA3ABeACAAdwBiAGdDJIBBTAuOC4ymAEAoAEByAEKwAEB&sclient=gws-wiz'
                url_m = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%BC%D0%BE%D0%BD%D0%B5%D1%80%D0%BE&client=ubuntu&hs=4eU&channel=fs&ei=y4MwYp62DMbrrgSFup7ICw&ved=0ahUKEwjex424jMj2AhXGtYsKHQWdB7kQ4dUDCA0&uact=5&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%BC%D0%BE%D0%BD%D0%B5%D1%80%D0%BE&gs_lcp=Cgdnd3Mtd2l6EAMyCggAEIAEEEYQggIyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQ6BwgAEEcQsAM6CggAEEcQsAMQyQM6BwgAELADEEM6EgguEMcBEKMCEMgDELADEEMYAToSCC4QxwEQ0QMQyAMQsAMQQxgBOgsIABCABBCxAxCDAUoECEEYAEoECEYYAFDFA1jUCWDTC2gBcAF4AIABpwGIAf8FkgEDMC42mAEAoAEByAENwAEB2gEECAEYCA&sclient=gws-wiz'
                url_g = 'https://www.google.com/search?q=%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&client=ubuntu&channel=fs&ei=76MwYuiiG-bhrgT-j57ICw&ved=0ahUKEwio1tGLq8j2AhXmsIsKHf6HB7kQ4dUDCA0&uact=5&oq=%D0%B3%D1%80%D0%B8%D0%B2%D0%BD%D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&gs_lcp=Cgdnd3Mtd2l6EAMyDwgAELEDEIMBEEMQRhCCAjIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoHCAAQRxCwAzoKCAAQRxCwAxDJAzoHCAAQsAMQQzoSCC4QxwEQowIQyAMQsAMQQxgBOhIILhDHARDRAxDIAxCwAxBDGAE6BggAEAcQHjoECAAQDUoECEEYAEoECEYYAFDCBVjYEGD4F2gBcAF4AIABwQKIAaAOkgEFMi01LjKYAQCgAQHIAQvAAQHaAQQIARgI&sclient=gws-wiz'
                source_d = requests.get(url_d, headers=headers)
                source_e = requests.get(url_e, headers=headers)
                source_b = requests.get(url_b, headers=headers)
                source_m = requests.get(url_m, headers=headers)
                source_g = requests.get(url_g, headers=headers)
                text_d = BeautifulSoup(source_d.content, 'html.parser')
                text_e = BeautifulSoup(source_e.content, 'html.parser')
                text_b = BeautifulSoup(source_b.content, 'html.parser')
                text_m = BeautifulSoup(source_m.content, 'html.parser')
                text_g = BeautifulSoup(source_g.content, 'html.parser')
                dollar = text_d.findAll("span", {'class': 'DFlfde SwHCTb'})
                Euro = text_e.findAll("span", {'class': 'DFlfde SwHCTb'})
                BtC = text_b.findAll("span", {'class': 'pclqee'})
                Monero = text_m.findAll("span", {'class': 'pclqee'})
                Grivna = text_g.findAll("span", {"class": "DFlfde SwHCTb"})
                timee()
                bot.send_message(m.chat.id, "Курсы на " + cur_date + " " + cur_time + "\n🇺🇸 Курс доллара: " +
                                dollar[0].text + '\n🇪🇺 Курс евро: ' + Euro[0].text + '\n ₿  Курс биткойна: ' +
								BtC[0].text + '\n🪙 Курс монеро: ' + Monero[0].text + '\n🇺🇦 Курс гривны: ' + Grivna[0].text)
            except Exception as err:
                timee()
                print("Курс валют | Ошибка вывода курса.", cur_date,
                    cur_time, '\nError:', traceback.format_exc())
                bot.send_message(m.chat.id, "Ошибка вывода курса валют.")
        elif m.text == '🪙 Орел и решка ❓':
            OaR = ['Решка.', 'Орёл.']
            bot.send_message(m.chat.id, 'Вам выпал(а): ' + random.choice(OaR))
        con.close()
    if __name__ == '__main__':
        bot.polling(none_stop=True, interval=0)


while True:
    try:
        main()
    except Exception as err:
        timee()
        print('Error! Restarting...', cur_date, cur_time,
            '\nError:', traceback.format_exc())
        time.sleep(3)
        continue
    else:
        print("\nStopped...")
        break