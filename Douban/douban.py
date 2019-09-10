import requests
import time
import pandas as pd
import random
from lxml import etree
from io import BytesIO
import jieba #中文分词库
from wordcloud import WordCloud
import numpy as np
from PIL import Image

class douban():
    def __init__(self):
        #定义session 用来加载HTML
        self.session = requests.session()
        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
        self.url_login = "https://www.douban.com/login"
        self.url_comment = 'https://movie.douban.com/subject/3230459/comments?start=%d&limit=20&sort=new_score&status=P'


    def scrapy(self):
        login_request = self.session.get(self.url_login,headers=self.header)
        #解析HTML
        selector = etree.HTML(login_request.content)
        post_data = {
            'source': 'None',  # 不需要改动
            'redir': 'https://www.douban.com',  # 不需要改动
            'form_email': '18846425113',  # 填账号
            'form_password': 'weng1321456',  # 填密码
            'login': '登录'
        }
        #下面是获取验证码图片的连接
        captcha_img_url = selector.xpath('//img[@id="captcha_image"]/@src')
        if captcha_img_url != []:
            pic_request = requests.get(captcha_img_url[0])
            img = Image.open(BytesIO(pic_request.content))
            img.show()
            #填写验证码
            string = input("请输入验证码：")
            post_data['captcha-solution'] = string
            captcha_id = selector.xpath('//input[@name="captcha-id"]/@value')
            post_data['captcha_id'] = captcha_id[0]
        self.session.post(self.url_login,data=post_data)
        print('已经登录豆瓣')

        users = []
        times = []
        stars = []
        comment_texts = []
        for i in range(0,500,20):
            data = self.session.get(self.url_comment % i,headers = self.header)
            print('状态码：',data.status_code)
            #暂停一下避免IP被封
            time.sleep(random.random())
            selector = etree.HTML(data.text)
            comments = selector.xpath('//div[@class="comment"]')

            for comment in comments:
                # 获取用户名
                user = comment.xpath('.//h3/span[2]/a/text()')[0]
                # 获取评星
                star = comment.xpath('.//h3/span[2]/span[2]/@class')[0][7:8]
                # 获取时间
                date_time = comment.xpath('.//h3/span[2]/span[3]/@title')
                # 有的时间为空，需要判断下
                if len(date_time) != 0:
                    date_time = date_time[0]
                else:
                    date_time = None
                # 获取评论文字
                comment_text = comment.xpath('.//p/span/text()')[0].strip()
                # 添加所有信息到列表，以下相同
                users.append(user)
                stars.append(star)
                times.append(date_time)
                comment_texts.append(comment_text)
                # 用字典包装
        comment_dic = {'user': users, 'star': stars, 'time': times, 'comments': comment_texts}
        comment_df = pd.DataFrame(comment_dic)  # 转换成DataFrame格式
        comment_df.to_csv('duye_comments.csv')  # 保存数据
        comment_df['comments'].to_csv('comment.csv', index=False)  # 将评论单独再保存下来，方便分词
        print(comment_df)

    def jieba_(self):
        content = open('comment.csv','r',encoding='utf-8').read()
        word_list = jieba.cut(content)
        with open('myword.txt') as f:
            jieba.load_userdict(f)
        word = []
        for i in word_list:
            with open('nothing.txt','r',encoding='UTF-8') as f:
                meaningless_file = f.read().splitlines()

                f.close()
            if i not in meaningless_file:
                word.append(i.replace(' ', ''))
        global word_cloud
        word_cloud = '.'.join(word)
        print(word_cloud)

    def word_cloud_(self):

        cloud_mask = np.array(Image.open('0.jpg'))
        wc = WordCloud(
            background_color="white",  # 背景图分割颜色为白色
            mask=cloud_mask,  # 背景图样
            max_words=300,  # 显示最大词数
            font_path='./fonts/simhei.ttf',  # 显示中文
            min_font_size=5,  # 最小尺寸
            max_font_size=100,  # 最大尺寸
            width=400  # 图幅宽度
        )
        global word_cloud
        x = wc.generate(word_cloud)
        image = x.to_image()
        image.show()
        wc.to_file('pic.png')


if __name__ == '__main__':
    s = Image.open('0.jpg')
    douban = douban()
    douban.scrapy()
    douban.jieba_()
    douban.word_cloud_()






