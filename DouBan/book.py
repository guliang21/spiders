"""
爬取豆瓣读书
"""

import os
import re
import random
import time
from urllib import parse
import requests
from bs4 import BeautifulSoup


def crawling(tag, url):
    print(f"正在爬取：{url}")
    start = parse.parse_qs(parse.urlparse(url).query).get('start')
    if start:
        start = int(start[0])
    else:
        start = 0

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    lis = soup.find_all('li', class_='subject-item')
    infos = []
    i = 1
    for li in lis:
        div = li.find('div', class_='info')
        index = start + i
        i += 1
        title = re.sub('\\s+', '', div.find('a').text)
        pub = div.find('div', class_='pub').text.strip().split('/')
        author = pub[0].strip()
        translator = ''
        if len(pub) == 5:
            # 译者不一定有
            translator = pub[1].strip()
        if len(pub) >= 4:
            publishing_house = pub[-3].strip()
            publication_date = pub[-2].strip()
            price = pub[-1].strip()
        else:
            # 有些情况只有一个书名，没有出版社、价格等信息
            publishing_house = ''
            publication_date = ''
            price = ''
        eRating = div.find('span', class_='rating_nums')
        # 少于10人评价是没有评分的
        if eRating:
            rating = eRating.text
        else:
            rating = ''
        number = re.sub('[\\s()]', '', div.find('span', class_='pl').text)
        infos.append((index, title, author, translator, publishing_house,
                      publication_date, price, rating, number))
    write_fo_file(tag, infos)

    thispage = soup.find('span', class_='thispage')
    if thispage:
        nextpage = thispage.find_next_sibling('a')
        if nextpage:
            time.sleep(random.randint(2, 10))
            nexturl = 'https://book.douban.com' + nextpage['href']
            crawling(tag, nexturl)


def write_fo_file(tag, infos):
    # 例如\u2022，GBK里是没有的，只能用UTF8
    f = open(f'{tag}.csv', 'a', encoding='utf-8')
    for info in infos:
        f.write(f'{info[0]},{info[1]},{info[2]},{info[3]},'
                f'{info[4]},{info[5]},{info[6]},{info[7]},{info[8]}\n')
    f.closed


def main():
    tags = ['编程']
    for tag in tags:
        if os.path.exists(f'{tag}.csv'):
            os.remove(f'{tag}.csv')
        crawling(tag, f'https://book.douban.com/tag/{tag}')
    print("爬取完毕。")


if __name__ == '__main__':
    main()
