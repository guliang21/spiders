# 打包 pyinstaller -F -p C:\Python37\Lib\site-packages cnblogs.py

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


class Dal:
    host = 'http://localhost:7010/'

    def SaveBlog(self, data):
        r = requests.post(self.host + 'api/blog', data=data)

    def SaveBlogReadedCount(self, data):
        r = requests.post(self.host + 'api/blogreadedcount', data=data)


r1 = re.compile('@\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}).*?阅读\s*\((\d+)\)')
r2 = re.compile('postid=(\d+)')
now = datetime.now()


def get_cnblogs(url):
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
                'Articleid': 'b' + r2.search(info_div.find('a')['href']).group(1),
                'PublishTime': m.group(1),
                'Title': title_div.text.strip(),
                'From': 'cnblogs'
            }
            blogReadedCount = {
                'CollectTime': now,
                'Articleid': blog['Articleid'],
                'ReadedCount': int(m.group(2))
            }
            print(
                f'{blog["Articleid"]:9}    {blog["PublishTime"]} {blogReadedCount["ReadedCount"]:7}    {blog["Title"]}')
            dal.SaveBlog(blog)
            dal.SaveBlogReadedCount(blogReadedCount)

    next_tab = soup.find('a', text=re.compile("下一页"))
    if next_tab is not None:
        next_url = next_tab['href']
        get_cnblogs(next_url)


def get_csdn(url, index):
    dal = Dal()

    r = requests.get(url + str(index))
    html = r.content.decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')

    tab_blogs = soup.find('div', class_='article-list')
    if tab_blogs:
        for tab_blog in tab_blogs.find_all('div', recursive=False, class_='article-item-box'):
            blog = {
                'Articleid': 'c' + tab_blog['data-articleid'],
                'PublishTime': tab_blog.find('span', class_='date').text.strip(),
                'Title': tab_blog.find('a').text.replace('原创', '').strip(),
                'From': 'csdn'
            }
            blogReadedCount = {
                'CollectTime': now,
                'Articleid': blog['Articleid'],
                'ReadedCount': int(tab_blog.find('span', class_='num').text.strip())
            }
            print(
                f'{blog["Articleid"]:10}    {blog["PublishTime"]} {blogReadedCount["ReadedCount"]:7}    {blog["Title"]}')
            dal.SaveBlog(blog)
            dal.SaveBlogReadedCount(blogReadedCount)

        index += 1
        get_csdn(url, index)


if __name__ == '__main__':
    get_cnblogs('https://www.cnblogs.com/gl1573/')
    get_csdn('https://blog.csdn.net/guliang21/article/list/', 1)

