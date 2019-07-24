from datetime import date
import logging
import os
from peewee import Model, SqliteDatabase, CharField, DateField, DateTimeField, IntegerField, CompositeKey

log = logging.getLogger('peewee')
log.setLevel(logging.ERROR)
log.parent = logging.getLogger('cnblogs')

db_path = 'cnblogs.db'


class BlogViews(Model):
    postId = IntegerField(verbose_name='博客ID')
    statisticsDate = DateField(verbose_name='统计日期', default=date.today())
    createTime = DateTimeField(verbose_name='发布时间')
    blogTitle = CharField(verbose_name='博客标题', max_length=200)
    readCount = IntegerField(verbose_name='阅读量')
    newCount = IntegerField(verbose_name='新增阅读量')

    class Meta:
        database = SqliteDatabase(db_path)
        primary_key = CompositeKey('postId', 'statisticsDate')

    def __str__(self):
        return f'{self.createTime}\t{"{:<8}".format(self.readCount)}{"{:<8}".format(self.newCount)}{self.blogTitle}'


class TotalViews(Model):
    statisticsDate = DateField(verbose_name='统计日期', default=date.today())
    totalCount = IntegerField(verbose_name='总阅读量')
    sumNewCount = IntegerField(verbose_name='新增阅读量')

    class Meta:
        database = SqliteDatabase(db_path)

    def __str__(self):
        return f'总阅读量：{self.totalCount},    新增阅读量：{self.sumNewCount}'


class ScoreRank(Model):
    statisticsDate = DateField(verbose_name='统计日期', default=date.today())
    score = IntegerField(verbose_name='得分')
    rank = IntegerField(verbose_name='排名')

    class Meta:
        database = SqliteDatabase(db_path)

    def __str__(self):
        return f'得分：{self.score},   排名：{self.rank}'


if not os.path.exists(db_path):
    BlogViews.create_table()
    TotalViews.create_table()
    ScoreRank.create_table()
