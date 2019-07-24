"""
黑板课爬虫闯关第二关
这一关需用输入用户名密码，密码是30以内的数字
枚举密码循环 post 请求，直到密码正确
"""

import re
import requests
import time


def main():
    url = 'http://www.heibanke.com/lesson/crawler_ex01/'
    for psd in range(30):
        print(f'test password {psd}')
        r = requests.post(url, data={'username': 'aa', 'password': psd})
        html = r.text
        if '密码错误' not in html:
            m = re.search('(?<=\<h3\>).*?(?=\</h3\>)', html)
            print(m.group())
            m = re.search('(\<).*?href="([^"]*?)".*?(\>下一关\</a\>)', html)
            print(f'下一关 http://www.heibanke.com{m.group(2)}')
            return
        else:
            time.sleep(1)


if __name__ == '__main__':
    main()
