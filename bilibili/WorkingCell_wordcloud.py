import csv
import jieba.analyse
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt


def get_texts():
    with open('WorkingCell.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        texts = ';'.join(row[1] for row in reader if len(row) > 2)
        return texts


cut_text = " ".join(jieba.cut(get_texts()))
keywords = jieba.analyse.extract_tags(cut_text, topK=500, withWeight=True, allowPOS=('a', 'e', 'n', 'nr', 'ns'))
text_cloud = dict(keywords)

bg = plt.imread("血小板.jpg")
# 生成
wc = WordCloud(
    background_color="white",  # 设置背景为白色，默认为黑色
    width=400,  # 设置图片的宽度
    height=600,  # 设置图片的高度
    mask=bg,
    random_state=2,
    max_font_size=500,  # 显示的最大的字体大小
    font_path="STSONG.TTF",
).generate_from_frequencies(text_cloud)
# 为图片设置字体

# 图片背景
bg_color = ImageColorGenerator(bg)
plt.imshow(wc.recolor(color_func=bg_color))
plt.imshow(wc)
# 为云图去掉坐标轴
plt.axis("off")
plt.show()
wc.to_file("词云.png")
