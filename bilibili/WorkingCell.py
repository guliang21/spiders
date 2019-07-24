"""
爬取 bilibili 《工作细胞》短评
短评为异步加载，通过分析
"""

import csv
import os
import time
import requests
from fake_useragent import UserAgent

curcount = 0


def main():
    url = 'https://bangumi.bilibili.com/review/web_api/short/list?media_id=102392&folded=0&page_size=20&sort=0'
    crawling(url)


def crawling(url):
    print(f'正在爬取：{url}')
    global curcount
    headers = {"User-Agent": UserAgent(verify_ssl=False).random}
    json_content = requests.get(url, headers).json()
    total = json_content['result']['total']
    infolist = []
    for item in json_content['result']['list']:
        info = {
            'author': item['author']['uname'],
            'content': item['content'],
            'ctime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['ctime'])),
            'likes': item['likes'],
            'disliked': item['disliked'],
            'score': item['user_rating']['score']
        }
        infolist.append(info)
    savefile(infolist)

    curcount += len(infolist)
    print(f'当前进度{curcount}/{total}')
    if curcount >= total:
        print('爬取完毕。')
        return

    nexturl = f'https://bangumi.bilibili.com/review/web_api/short/list?' \
              f'media_id=102392&folded=0&page_size=20&sort=0&cursor={json_content["result"]["list"][-1]["cursor"]}'
    time.sleep(1)
    crawling(nexturl)


def savefile(infos):
    with open('WorkingCell.csv', 'a', encoding='utf-8') as sw:
        fieldnames = ['author', 'content', 'ctime', 'likes', 'disliked', 'score']
        writer = csv.DictWriter(sw, fieldnames=fieldnames)
        writer.writerows(infos)


if __name__ == '__main__':
    if os.path.exists('WorkingCell.csv'):
        os.remove('WorkingCell.csv')
    main()
