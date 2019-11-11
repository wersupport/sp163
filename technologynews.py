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

#wordpress 链接
client = Client('https://atvnet.com.au/xmlrpc.php', 'South Tao', 'king001002003!')
#图片储存位置
pathtemp = os.path.abspath(os.path.dirname(__file__))
path=os.path.join(pathtemp,'imgtech')
#内容提取链接
url = 'https://tech.163.com/special/00097UHL/tech_datalist.js?callback=data_callback'


#常量  n为图片前缀,timeout 为等待时间,
n=0
timeout = 20
socket.setdefaulttimeout(timeout)
sleep_download_time = 5

#tobewirtedcsvdata 是要写入CSV的列表 titlelist是题目与图片对比时的列表
tobewirtedcsvdata = []

# 构造头部
ua_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]
user_agent = random.choice(ua_list)

# 返回url 对应的json
def getJsonContent(url):

    req = urllib2.Request(url=url)
    req.add_header('User-Agent', user_agent)
    response = urllib2.urlopen(req)
    content = response.read().decode('gbk').replace('data_callback(', '').replace(')', '')
    jscontents = json.loads(content, strict=False)

    return jscontents

# passed print test print(getJsonContent(url))

# 1 获得内容页面tag对象, 返回一个tag对象
def detailPage(url):

    # 详细页面的url request
    try:
        req1 = urllib2.Request(url=url)
        req1.add_header('User-Agent', user_agent)
        # urlopen 打开
        detailreq = urllib2.urlopen(req1)
        detailcontent = detailreq.read().decode('gb18030', errors='ignore')
        # 取到beautifulsoup 的对象
        detailobj = BeautifulSoup(detailcontent, 'html5lib')
        time.sleep(sleep_download_time)
        detailreq.close()
        return detailobj
    except:
        print('decode or open url error')
        pass


# 2 获取对象中的标题
def getTitle(obj):
    # 取文章标题
    try:
        detailTitle = obj.find(name='div',class_='post_content_main').h1.getText()
        return detailTitle
    except:
        print('no title fetched')
        pass

# 3 获取对象中的图片链接
def getImgurl(obj, featuredimageurl):
    # "get first image"
    try:
        detailImgurl = obj.find(name='p', class_='f_center').img.get('src')
    except:
        detailImgurl = featuredimageurl
    return detailImgurl
# 4 获取对象的正文html
def getContent(obj,sourceurl):
    try:
        detailinnerHtml = obj.find(name='div', class_='post_text')
        originaltitleHtml = obj.find(name='p', class_='otitle')
        # 广告内容
        adshtml = obj.find(name='div', class_='gg200x300')

        # 获得来源div - delete later, source editor
        sourcediv = obj.find(name='div', class_='ep-source cDGray')

        source = obj.find(name='span', class_='left').getText()
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
        finalContent = part1.replace(part4, ' ').replace(part2, '<br>').replace(part3,
                                                                                " ") + '<p><a href=%s  target="_blank">' % (
                           sourceurl) + source + '</a></p>'

    except:
        finalContent = None
        print('error happen, finalcontent is none')
        pass

    return finalContent

# 5 Store uploade the Image
def upLoadToWp(title, toBeUsedImgUrl, toBeUsedContent, n, keywords1,keywords2,keywords3,):

    # Part 1 Image download and write to file
    reqimg = urllib2.Request(url=toBeUsedImgUrl)
    reqimg.add_header('User-Agent', user_agent)
    img = urllib2.urlopen(reqimg).read()
    # 取图片后缀名
    if re.search('jpg', toBeUsedImgUrl):
        extentionname = re.search('jpg', toBeUsedImgUrl).group()
    elif re.search('jpeg', toBeUsedImgUrl):
        extentionname = re.search('jpeg', toBeUsedImgUrl).group()
    elif re.search('png', toBeUsedImgUrl):
        extentionname = re.search('png', toBeUsedImgUrl).group()
    elif re.search('gif', toBeUsedImgUrl):
        extentionname = re.search('gif', toBeUsedImgUrl).group()
    else:
        extentionname = re.search('jpg', toBeUsedImgUrl).group()

    imgName = str(n) + '-' + keywords1 + '-' + keywords2 + '.' + extentionname
    imgPath = os.path.join(path, imgName)

    # 写入图片
    with open(imgPath, 'wb') as f:
        f.write(img)
        f.close()
    print(n, imgPath)

    templist = [n, title, imgPath, toBeUsedContent, keywords1, keywords2, keywords3]

    # 构造post, 图片metadata, 发布post
    try:
        data = {
            'name': imgName,
            'type': mimetypes.guess_type(imgPath)[0],  # mimetype
        }
        with open(imgPath, 'rb') as img:
            data['bits'] = xmlrpc_client.Binary(img.read())

        response = client.call(media.UploadFile(data))
        attachmentID = response['id']

        post = WordPressPost()
        post.title = title
        post.content = toBeUsedContent
        post.post_status = 'draft'
        post.excerpt = title + '-' + keywords1 + '-' + keywords2 + '-'+keywords3+'-' + '亚太商业网络'

        post.terms_names = {
            'post_tag': [keywords3, keywords2, keywords1],
            'category': ['新闻']
        }
        post.thumbnail = attachmentID
        post.id = client.call(posts.NewPost(post))
        return templist

    except:
        print(str(n) + ' have a error')
        pass


# 6 获取全部信息 等待上传
def cookUsefulInfo(detailContentObj,n,keywords1,keywords2,keywords3,contentUrl,featuredimageurl):
    title = getTitle(detailContentObj)
    toBeUsedImgUrl = getImgurl(detailContentObj,featuredimageurl)
    toBeUsedContent = getContent(detailContentObj,contentUrl)

    upLoadToWp(title,toBeUsedImgUrl, toBeUsedContent, n, keywords1,keywords2,keywords3,)

    return title,toBeUsedImgUrl,toBeUsedContent

def mainFunc(jsDatas,n):

    for jscontent in jsDatas:

        contentUrl=jscontent['docurl']
        imageUrl=jscontent['imgurl']
        contentType=jscontent['newstype']

        if len(jscontent['keywords'])>=2:
            keywords1 =jscontent['keywords'][0]['keyname']
            keywords2 =jscontent['keywords'][1]['keyname']
            keywords3 = jscontent['label']
        else:
            keywords1 = '亚太新闻'
            keywords2 = 'Technology'
            keywords3 = '互联网'

        if contentType == 'photoset':
            print(str(n) + 'is photoset, passed')
        else:
            detailContentObj = detailPage(contentUrl)
            print(n,contentUrl,imageUrl)
            cookUsefulInfo(detailContentObj,n,keywords1,keywords2,keywords3,contentUrl,imageUrl)
        n+=1
        pass



if __name__ == '__main__':
    mainFunc(getJsonContent(url),n)