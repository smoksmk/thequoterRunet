#!/usr/bin/python3
# -*- coding: utf-8 -*-

#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup

def get_html(url):
    r = requests.get(url)
    return r.text

def get_data(html):
    soup = BeautifulSoup(html, "lxml")
    div = soup.find_all('div', class_="quote")
    result = [{i.find('a', class_='id').text: i.find("div", class_="text").text} for i in div]
    return result



def main():
    html = get_html("http://bash.im/")
    get_data(html)


if __name__ == '__main__':
    main()