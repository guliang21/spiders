"""
黑板课爬虫闯关第五关
验证码识别
"""

import re
import requests
import time
from PIL import Image
from bs4 import BeautifulSoup
import tesserocr


def main():
    url_login = 'http://www.heibanke.com/accounts/login/'
    url = 'http://www.heibanke.com/lesson/crawler_ex04/'
    session = requests.Session()
    session.get(url_login)
    token = session.cookies['csrftoken']
    session.post(url_login, data={'csrfmiddlewaretoken': token, 'username': 'guliang21', 'password': '123qwe'})
    psd = 0
    while psd < 30:
        print(f'test password {psd}')
        r = session.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        img_tag = soup.find('img')
        img_url = 'http://www.heibanke.com' + img_tag['src']
        requests.get(url)
        code = get_code(img_url)
        if code is None:
            time.sleep(1)
            continue
        token = session.cookies['csrftoken']
        r = session.post(url, data={'csrfmiddlewaretoken': token, 'username': 'aa', 'password': psd,
                                    'captcha_0': code[0], 'captcha_1': code[1]})
        html = r.text
        if '验证码输入错误' in html:
            time.sleep(1)
        elif '密码错误' not in html:
            m = re.search('(?<=\<h3\>).*?(?=\</h3\>)', html)
            print(m.group())
            return
        else:
            time.sleep(1)
            psd += 1


def get_code(url):
    flag = url.split("/")[-2]
    fn = flag + '.png'
    with open(fn, 'wb+') as sw:
        sw.write(requests.get(url).content)

    img = Image.open(fn)
    img = img.convert('L')
    # table = [0 if i < 127 else 1 for i in range(256)]
    # img = img.point(table, '1')
    result = tesserocr.image_to_text(img).strip()
    print(flag, result)
    if re.match('^[A-Za-z0-9]{4}$', result):
        return flag, result


if __name__ == '__main__':
    main()
