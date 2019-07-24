"""
爬取猫眼2018电影
破解字体反爬
"""


import os
import time
import re
import requests
from fontTools.ttLib import TTFont
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

host = 'http://maoyan.com'


def main():
    url = 'https://maoyan.com/films?yearId=14'
    get_moviescore(url)


os.makedirs('font', exist_ok=True)
regex_woff = re.compile("(?<=url\(').*\.woff(?='\))")
regex_text = re.compile('(?<=<span class="stonefont">).*?(?=</span>)')
regex_font = re.compile('(?<=&#x).{4}(?=;)')

basefont = TTFont('base.woff')
fontdict = {'uniF30D': '0', 'uniE6A2': '8', 'uniEA94': '9', 'uniE9B1': '2', 'uniF620': '6',
            'uniEA56': '3', 'uniEF24': '1', 'uniF53E': '4', 'uniF170': '5', 'uniEE37': '7'}


def get_moviescore(url):
    # headers = {"User-Agent": UserAgent(verify_ssl=False).random}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/68.0.3440.106 Safari/537.36'}
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    ddlist = soup.find_all('dd')
    for dd in ddlist:
        a = dd.find('a')
        if a is not None:
            link = host + a['href']
            time.sleep(5)
            dhtml = requests.get(link, headers=headers).text
            msg = {}

            dsoup = BeautifulSoup(dhtml, 'lxml')
            msg['name'] = dsoup.find(class_='name').text
            ell = dsoup.find_all('li', {'class': 'ellipsis'})
            msg['type'] = ell[0].text
            msg['country'] = ell[1].text.split('/')[0].strip()
            msg['length'] = ell[1].text.split('/')[1].strip()
            msg['release-time'] = ell[2].text[:10]

            # 下载字体文件
            woff = regex_woff.search(dhtml).group()
            wofflink = 'http:' + woff
            localname = 'font\\' + os.path.basename(wofflink)
            if not os.path.exists(localname):
                downloads(wofflink, localname)
            font = TTFont(localname)

            # 其中含有 unicode 字符，BeautifulSoup 无法正常显示，只能用原始文本通过正则获取
            ms = regex_text.findall(dhtml)
            if len(ms) < 3:
                msg['score'] = '0'
                msg['score-num'] = '0'
                msg['box-office'] = '0'
            else:
                msg['score'] = get_fontnumber(font, ms[0])
                msg['score-num'] = get_fontnumber(font, ms[1])
                msg['box-office'] = get_fontnumber(font, ms[2]) + dsoup.find('span', class_='unit').text
            print(msg)


def get_fontnumber(newfont, text):
    ms = regex_font.findall(text)
    for m in ms:
        text = text.replace(f'&#x{m};', get_num(newfont, f'uni{m.upper()}'))
    return text


def get_num(newfont, name):
    uni = newfont['glyf'][name]
    for k, v in fontdict.items():
        if uni == basefont['glyf'][k]:
            return v


def downloads(url, localfn):
    with open(localfn, 'wb+') as sw:
        sw.write(requests.get(url).content)


if __name__ == '__main__':
    main()
