#coding:utf-8
import urllib.request as urllib2
import random
from bs4 import BeautifulSoup
from datetime import date
import csv
import socket
import os
import re
import time
import json

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.methods import taxonomies
from wordpress_xmlrpc import WordPressTerm
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media,posts

import mimetypes


#wordpress client
client = Client('https://atvnet.com.au/xmlrpc.php', 'South Tao', 'king001002003!')

#写入title
filetitle= date.today().strftime("%d%m%y")+'technews'+'.csv'


#PART 1 定义常亮,模拟header,本地路径,休息时间,爬取url等

pathtemp = os.path.abspath(os.path.dirname(__file__))
path=os.path.join(pathtemp,'imgfin')

url = 'https://money.163.com/special/00259BVP/news_flow_index.js?callback=data_callback'
imageUrl='https://money.163.com/'
n=0
timeout = 10
tobewirtedcsvdata = []
titlelist = []
socket.setdefaulttimeout(timeout)
sleep_download_time = 5

#构造头部
ua_list = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]

user_agent = random.choice(ua_list)
req = urllib2.Request(url=url)
req.add_header('User-Agent', user_agent)


#PART 2 得到返回值
response = urllib2.urlopen(req)
content = response.read().decode('gbk').replace('data_callback(','').replace(')','')
#jscontents is a List
jscontents = json.loads(content,strict=False)


#PART 4 具体的页面，写入 CSV，下载图片

#4.1 获得内容页面tag对象, 返回一个tag对象
def detailPage(url):
    #详细页面的url request
    req1 = urllib2.Request(url=url)
    req1.add_header('User-Agent', user_agent)
    #urlopen 打开
    detailreq = urllib2.urlopen(req1)
    detailcontent = detailreq.read().decode('gb18030')
    # 取到beautifulsoup 的对象
    detailobj = BeautifulSoup(detailcontent,'html5lib')
    time.sleep(sleep_download_time)
    detailreq.close()
    return detailobj


#4.2 获取对象中的标题
def getTitle(obj):
    # 取文章标题
    detailTitle = obj.find(name='div',class_='post_content_main').h1.getText()
    return detailTitle

#4.3 获取对象中的图片链接
def getImgurl(obj):
    #get first image
    try:
        detailImgurl = obj.find(name='p', class_='f_center').img.get('src')
    except:
        detailImgurl = "noimage"
    return detailImgurl


#4.4 获取对象的正文html
def getContent(obj,sourceurl):
    try:
        detailinnerHtml = obj.find(name='div',class_='post_text')
        originaltitleHtml = obj.find(name='p',class_='otitle')
        #广告内容
        adshtml= obj.find(name='div',class_='gg200x300')

        #获得来源div - delete later, source editor
        sourcediv = obj.find(name='div',class_='ep-source cDGray')

        source = obj.find(name='span',class_='left').getText()
        '''
        得出完美的内容 字符串处理
        part 1 - 原始的全部字符串
        part 2 - 广告块
        part 3 - 作者块
        finalContent=  处理完ready to use的
        '''
        part1 = str(detailinnerHtml)
        part2 = str(adshtml)
        part3 = str(sourcediv)
        part4 = str(originaltitleHtml)
        finalContent = part1.replace(part4,' ').replace(part2,'<br>').replace(part3," ") + '<p><a href=%s  target="_blank">'%(sourceurl)+source+'</a></p>'

    except:
        finalContent = None
        pass



    return finalContent

# 写入列表 写入图片 写入xmlrpc
def getuseinfo(obj,n,key1,key2,key3,title,contentUrl):
    if key3 == '图集':
        pass
    else:
        b = getImgurl(obj)
        c = getContent(obj,contentUrl)

        if b != 'noimage':
            d=b
        else:
            d = 'https://atvnet.com.au/wp-content/uploads/2019/06/logo-retina.png'

        reqimg = urllib2.Request(url=d)
        reqimg.add_header('User-Agent', user_agent)

        img = urllib2.urlopen(reqimg).read()
        print(d)

        #取图片后缀名
        if re.search('jpg',d):
            extentionname = re.search('jpg',d).group()

        elif re.search('jpeg',d):
            extentionname = re.search('jpeg',d).group()

        elif re.search('png',d):
            extentionname = re.search('png',d).group()

        elif re.search('gif',d) :
            extentionname = re.search('gif',d).group()

        else:
            extentionname = re.search('jpg',d).group()


        #print(extentionname)
        imgName =  str(n)+'-'+key1+'-'+key2+ '.'+extentionname
        imgPath= os.path.join(path,imgName)


        #写入图片
        with open(imgPath, 'wb') as f:
            f.write(img)
            f.close()
        print(n,imgPath)
        #写入列表
        templist = [n,title,b,c,key1,key2,key3]
        print(templist)

        #构造post, 图片metadata, 发布post
        try:
            data = {
                'name': imgName,
                'type':mimetypes.guess_type(imgPath)[0],  # mimetype
            }
            with open(imgPath, 'rb') as img:
                data['bits'] = xmlrpc_client.Binary(img.read())

            response = client.call(media.UploadFile(data))
            attachmentID= response['id']



            post = WordPressPost()
            post.title=title
            post.content = c
            post.post_status  = 'draft'
            post.excerpt = title+'-'+key1+'-'+key2+'-'+'亚太商业网络'

            post.terms_names ={
                'post_tag': [key1,key2,key3],
                'category':['新闻']
            }
            post.thumbnail = attachmentID
            post.id=client.call(posts.NewPost(post))

            return templist
        except:
            print (str(n) + ' have a error')
            pass



#PART 3 遍历，取值

for jscontent in jscontents:

    title = jscontent['title']
    contentUrl=jscontent['docurl']
    titlelist = titlelist.append(title)

    if len(jscontent['keywords'])>=2:
        keywords1 =jscontent['keywords'][0]['keyname']
        keywords2 =jscontent['keywords'][1]['keyname']
        keywords3 = jscontent['label']
    else:
        keywords1 = '财经新闻'
        keywords2 = 'Business'
        keywords3 = '商业'

    detailContentObj = detailPage(contentUrl)
    print(n,contentUrl)
    finallist = getuseinfo(detailContentObj,n,keywords1,keywords2,keywords3,title,contentUrl)
    n+=1
    pass



