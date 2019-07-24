"""
黑板课爬虫闯关第三关
这一关开始略有难度了
首先必须先注册用户，登录后方可继续
有个防 CSRF 攻击
同第二关，猜对密码即过关，但不同的是，必须是在登录状态下进行
"""

import re
import requests
import time


def main():
    url_login = 'http://www.heibanke.com/accounts/login/?next=/lesson/crawler_ex02/'
    url = 'http://www.heibanke.com/lesson/crawler_ex02/'
    session = requests.Session()
    # 获取cookie
    session.get(url_login)
    token = session.cookies['csrftoken']
    # 登录
    session.post(url_login, data={'csrfmiddlewaretoken': token, 'username': 'guliang21', 'password': '123qwe'})
    for psd in range(30):
        print(f'test password {psd}')
        session.get(url)
        token = session.cookies['csrftoken']
        r = session.post(url, data={'csrfmiddlewaretoken': token, 'username': 'aa', 'password': psd})
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
