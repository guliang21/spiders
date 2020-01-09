# 打包 pyinstaller -F -p C:\Python37\Lib\site-packages cnblogs.py

import requests
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime

log = logging.getLogger('cnblogs')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class Dal:
    host = 'http://localhost:7010/'

    def SaveBlog(self, data):
        r = requests.post(self.host + 'api/blog', data=data)

    def SaveBlogReadedCount(self, data):
        r = requests.post(self.host + 'api/blogreadedcount', data=data)


r1 = re.compile('@\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}).*?阅读\s*\((\d+)\)')
r2 = re.compile('postid=(\d+)')


def run(url):
    dal = Dal()

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    # 这是每天的一个 div，如果某天有多篇博客发布，则全包含在里面
    tab_blogs = soup.find_all('div', class_='day')
    for tab_blog in tab_blogs:
        tab_postTitles = tab_blog.find_all('div', class_='postTitle')
        tab_postDescs = tab_blog.find_all('div', class_='postDesc')
        for title_div, info_div in zip(tab_postTitles, tab_postDescs):
            m = r1.search(info_div.text.strip())

            blog = {
                'Articleid': int(r2.search(info_div.find('a')['href']).group(1)),
                'PublishTime': m.group(1),
                'Title': title_div.text.strip(),
                'From': 'cnblogs'
            }

            blogReadedCount = {
                'CollectTime': datetime.now(),
                'Articleid': blog['Articleid'],
                'ReadedCount': int(m.group(2))
            }

            log.debug(f'{blog["Articleid"]} {blog["PublishTime"]} {blogReadedCount["ReadedCount"]} {blog["Title"]}')

            dal.SaveBlog(blog)
            dal.SaveBlogReadedCount(blogReadedCount)

    next_tab = soup.find('a', text=re.compile("下一页"))
    if next_tab is not None:
        next_url = next_tab['href']
        run(next_url)


if __name__ == '__main__':
    run('https://www.cnblogs.com/gl1573/')
