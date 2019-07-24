"""
黑板课爬虫闯关第四关
密码一共100位，密码表中列出了每一位密码的值
但是网站加了限制，密码表网页打开很慢，主要目的是为了让我们使用多线程
但是黑板客服务器15秒内最多响应2个请求，否则返回404
"""

import re
import threading
import time
import requests
from bs4 import BeautifulSoup


pwlist = [-1 for i in range(100)]
count = 0
lock = threading.Lock()


def main():
    url_login = 'http://www.heibanke.com/accounts/login/?next=/lesson/crawler_ex03/'
    url = 'http://www.heibanke.com/lesson/crawler_ex03/'
    session = requests.Session()
    # 获取cookie
    session.get(url_login)
    token = session.cookies['csrftoken']
    # 登录
    session.post(url_login, data={'csrfmiddlewaretoken': token, 'username': 'oo', 'password': 'xx'})
    # 黑板客服务器15秒内最多响应2个请求，否则返回404.
    threadlist = [threading.Thread(target=getpw, args=(session,)) for _ in range(2)]
    for thread in threadlist:
        thread.setDaemon(True)
        thread.start()
    for thread in threadlist:
        thread.join()
    psd = ''.join(pwlist)
    print(f'密码：{psd}')
    session.get(url)
    token = session.cookies['csrftoken']
    r = session.post(url, data={'csrfmiddlewaretoken': token, 'username': 'aa', 'password': psd})
    html = r.text
    if '密码错误' not in html:
        m = re.search('(?<=\<h3\>).*?(?=\</h3\>)', html)
        print(m.group())


def getpw(session):
    pw_url = 'http://www.heibanke.com/lesson/crawler_ex03/pw_list/'
    global count, pwlist
    while count < 100:
        try:
            html = session.get(pw_url).text
        except:
            time.sleep(1)
            continue
        if '404 Not Found' in html:
            continue
        soup = BeautifulSoup(html, 'lxml')
        pos = soup.find_all('td', {'title': 'password_pos'})
        val = soup.find_all('td', {'title': 'password_val'})
        for i in range(len(pos)):
            p = int(pos[i].string)
            v = val[i].string
            lock.acquire()
            if pwlist[p - 1] == -1:
                pwlist[p - 1] = v
                count += 1
            lock.release()


if __name__ == '__main__':
    main()
