"""
爬取豆瓣电影Top250
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup


def download(url, page):
    print(f"正在爬取：{url}")
    html = requests.get(url).text   # 这里不加text返回<Response [200]>
    soup = BeautifulSoup(html, 'lxml')
    lis = soup.select("ol li")
    for li in lis:
        index = li.find('em').text
        title = li.find('span', class_='title').text
        rating = li.find('span', class_='rating_num').text
        strInfo = re.search("(?<=<br/>).*?(?=<)", str(li.select_one(".bd p")), re.S | re.M).group().strip()
        infos = strInfo.split('/')
        year = infos[0].strip()
        area = infos[1].strip()
        type = infos[2].strip()
        write_fo_file(index, title, rating, year, area, type)
    page += 25
    if page < 250:
        time.sleep(2)
        download(f"https://movie.douban.com/top250?start={page}&filter=", page)


def write_fo_file(index, title, rating, year, area, type):
    f = open('movie_top250.csv', 'a')
    f.write(f'{index},{title},{rating},{year},{area},{type}\n')
    f.closed


def main():
    if os.path.exists('movie_top250.csv'):
        os.remove('movie_top250.csv')

    url = 'https://movie.douban.com/top250'
    download(url, 0)
    print("爬取完毕。")


if __name__ == '__main__':
    main()
