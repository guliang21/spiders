import requests
from bs4 import BeautifulSoup
import logging
import re
from dal import BlogViews, TotalViews, ScoreRank
from datetime import date, timedelta
import matplotlib.pyplot as plt


log = logging.getLogger('cnblogs')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


r1 = re.compile('@\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}).*?阅读\((\d+)\)')
r2 = re.compile('postid=(\d+)')

cnblogs = []


def run(url):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    # 这是每天的一个 div，如果某天有多篇博客发布，则全包含在里面
    tab_blogs = soup.find_all('div', class_='day')
    for tab_blog in tab_blogs:
        tab_postTitles = tab_blog.find_all('div', class_='postTitle')
        tab_postDescs = tab_blog.find_all('div', class_='postDesc')
        for title_div, info_div in zip(tab_postTitles, tab_postDescs):
            blog = BlogViews()
            blog.blogTitle = title_div.text.strip()
            m = r1.search(info_div.text)
            blog.createTime = m.group(1)
            blog.readCount = int(m.group(2))
            blog.postId = int(r2.search(info_div.find('a')['href']).group(1))

            b = BlogViews.get_or_none((BlogViews.postId == blog.postId) & (BlogViews.statisticsDate == today))
            last = BlogViews.get_or_none((BlogViews.postId == blog.postId) & (BlogViews.statisticsDate == yesterday))
            if last:
                blog.newCount = blog.readCount - last.readCount
            else:
                blog.newCount = blog.readCount

            if b:
                if b.readCount != blog.readCount:
                    blog.save()
            else:
                blog.save(force_insert=True)
            cnblogs.append(blog)
            log.debug(blog)
    next_tab = soup.find('a', text='下一页')
    if next_tab is not None:
        next_url = next_tab['href']
        run(next_url)


# 要显示了积分和排名才可以抓取
def get_score_rank(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    score_str = soup.find(class_='liScore').text.strip()
    rank_str = soup.find(class_='liRank').text.strip()
    score = int(re.search('\d+', score_str).group())
    rank = int(re.search('\d+', rank_str).group())
    scoreRank = ScoreRank.get_or_none(ScoreRank.statisticsDate == date.today())
    if scoreRank:
        if scoreRank.score != score or scoreRank.rank != rank:
            ScoreRank.update(score=score, rank=rank).where(ScoreRank.statisticsDate == date.today()).execute()
    else:
        ScoreRank.insert(score=score, rank=rank).execute()
    log.debug(f'得分：{score},   排名：{rank}')


def sort_sum_count(blog):
    return blog.readCount


def sort_new_count(blog):
    return blog.newCount


def show_sum():
    sum_count = sum([blog.readCount for blog in cnblogs])
    sum_new_count = sum([blog.newCount for blog in cnblogs])

    totalViews = TotalViews.get_or_none(TotalViews.statisticsDate == date.today())
    if totalViews:
        if totalViews.totalCount != sum_count or totalViews.sumNewCount != sum_new_count:
            TotalViews.update(totalCount=sum_count, sumNewCount=sum_new_count) \
                .where(TotalViews.statisticsDate == date.today()).execute()
    else:
        TotalViews.insert(totalCount=sum_count, sumNewCount=sum_new_count).execute()

    log.debug(f'总阅读量：{sum_count},    新增阅读量：{sum_new_count}')

    get_score_rank('https://www.cnblogs.com/gl1573/mvc/blog/sidecolumn.aspx?blogApp=gl1573')

    log.debug('\n阅读排行榜：')
    for i, b in enumerate(sorted(cnblogs, key=sort_sum_count, reverse=True)[0: 10]):
        log.debug(f'{i + 1}\t{b}')

    log.debug('\n增量排行榜：')
    for i, b in enumerate(sorted(cnblogs, key=sort_new_count, reverse=True)[0: 10]):
        log.debug(f'{i + 1}\t{b}')


def draw():
    pass


if __name__ == '__main__':
    run('https://www.cnblogs.com/gl1573/')
    show_sum()
