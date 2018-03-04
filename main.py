#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging, config, datetime, requests, telebot, re
from time import sleep
from bs4 import BeautifulSoup


bot = telebot.TeleBot(config.TELEGRAM_KEY)


SINGLE_RUN = True

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    r = requests.get(url, headers=headers)
    return r.text

def get_int_id(value):
    digit = "[^\d]"
    data = int(re.sub(digit, "", value))
    return data

def parse_bashim():
    try:
        html = get_html("http://bash.im/")
        soup = BeautifulSoup(html, "lxml")
        div = soup.find_all('div', class_="quote")
        result = [{"id": get_int_id(i.find('a', class_='id').text),
                   'text': i.find("div", class_="text").text
                   } for i in div]

        return result
    except TimeoutError:
        return None

def send_message(arr_data, last_id):
    for data in arr_data:
        if int(data["id"]) <= int(last_id):
            continue
        # Рассылаем в группу
        logging.info(data['text'])
        bot.send_message(config.TELEGRAM_GROUP, data['text'])
        # Спим секунду чтобы не забанили и не наложили ограничения
        sleep(1)

def main():
    logging.info('Запуск Получения новых постов')
    with open(config.BASHIM_FILE_NAME, 'rt') as file:
        last_id = int(file.read())
        if last_id is None:
            logging.error('Не возможно получить поста ID поста')
            return
        logging.info('Последней ID поста = {!s}'.format(last_id))

    try:
        feed = parse_bashim()

        # Если ранее случился таймаут, пропускаем итерацию. Если всё нормально - парсим посты.
        if feed is not None:
            send_message(feed, last_id)
            # Записываем новый last_id в файл.
            with open(config.BASHIM_FILE_NAME, 'wt') as file:
                file.write(str(feed[0]["id"]))
                logging.info('ID Последнего поста: {!s}'.format((feed[0]["id"])))

    except Exception as ex:
        logging.error('Exception of type {!s} in get_data(): {!s}'.format(type(ex).__name__, str(ex)))
    logging.info('Завершение проверки новых постов')
    return


if __name__ == "__main__":
    # Избавляемся от спама в логах от библиотеки requests
    logging.getLogger('requests').setLevel(logging.CRITICAL)

    # Настраиваем наш логгер
    logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO,
                        # filename='bot_log.log',
                        datefmt='%d.%m.%Y %H:%M:%S')

    if not SINGLE_RUN:
        while True:
            main()
            # Пауза в 4 минуты перед повторной проверкой
            logging.info('[App] Script went to sleep.')
            sleep(60 * 4)
    else:
        main()
    logging.info('[App] Script exited.\n')