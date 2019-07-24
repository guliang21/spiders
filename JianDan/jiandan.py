"""爬取煎蛋妹子图"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import re
import os


browser = webdriver.Chrome()
# 设置网站等待时间
wait = WebDriverWait(browser, 10)


def get_html(url):
    print('正在爬取  %s' % url)
    try:
        browser.get(url)
        html = browser.page_source
        if html:
            return html
    except EOFError:
        return None


def download_img(html):
    soup = BeautifulSoup(html, 'lxml')
    curpage = soup.find('span', class_="current-comment-page")
    pageIndex = re.search("\\d+", curpage.text).group()
    nextpage = curpage.find_next_sibling('a')
    imgs = soup.find(class_='commentlist').find_all('img')
    count = 0
    for img in imgs:
        img_url = img['src']
        if img_url[-3:] == 'jpg':
            print('正在下载[%s]：%s 第 %s 张' % (pageIndex, img_url, count))
            write_fo_file(img_url, pageIndex, count)
            count += 1

    if nextpage:
        href = nextpage['href']
        return 'https:' + href


def write_fo_file(url, num, count):
    dirName = '{}/{}'.format('img', num)
    if not os.path.exists(dirName):
        os.makedirs(dirName)

    filename = '%s/%s/%s_%s.jpg' % (os.path.abspath('.'), dirName, num, count)
    with open(filename, 'wb+') as jpg:
        jpg.write(requests.get(url).content)


def next(url):
    html = get_html(url)
    next_url = download_img(html)
    if next_url:
        next(next_url)


def main():
    url = 'https://jandan.net/ooxx/'
    next(url)
    print('爬取完毕。')


if __name__ == '__main__':
    main()
