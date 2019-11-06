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

#PART 1 定义常亮,模拟header,本地路径,休息时间,爬取url等

path = os.path.abspath(os.path.dirname(__file__))
url = 'https://tech.163.com/special/00097UHL/tech_datalist.js?callback=data_callback'
n=0
timeout = 10
tobewirtedcsvdata = []
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
    detailcontent = detailreq.read().decode('gbk')
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
        detailImgurl = "https://atvnet.com.au/wp-content/uploads/2019/06/logo-retina.png"


    return detailImgurl


#4.4 获取对象的正文html
def getContent(obj):
    try:
        detailinnerHtml = obj.find(name='div',class_='post_text')

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
        finalContent = part1.replace(part2,'<br>').replace(part3," ") + '<p>'+source+'</p>'


    except:
        finalContent = None
        pass



    return finalContent

# 写入列表 写入图片 写入文件
def getuseinfo(obj,n,key1,key2,key3,title):

    b = getImgurl(obj)
    c = getContent(obj)

    reqimg= urllib2.Request(url=b)
    reqimg.add_header('User-Agent', user_agent)

    img = urllib2.urlopen(reqimg).read()

    #取图片后缀名
    if re.search('jpg',b):
        extentionname = re.search('jpg',b).group()
    elif re.search('jpeg',b):
        extentionname = re.search('jpeg',b).group()
    elif re.search('png',b):
        extentionname = re.search('png',b).group()
    elif re.search('gif',b) :
        extentionname = re.search('gif',b).group()
    else:
        extentionname = re.search('jpg',b).group()

    #print(extentionname)
    imgName =  str(n)+ '.'+extentionname
    imgPath= os.path.join(path,imgName)
    #print(imgPath)

    #写入图片
    with open(imgPath, 'wb') as f:
        f.write(img)

        f.close()

    #写入列表
    templist = [n,title,b,c,key1,key2,key3]
    tobewirtedcsvdata.append(templist)
    pushintoCSV(templist)
    #print(tobewirtedcsvdata)
    return tobewirtedcsvdata

#写入 csv
def pushintoCSV(list):

    title= date.today().strftime("%d%m%y")+'.csv'
    with open(title,'a+',encoding='utf-8-sig') as f:
        fcsv = csv.writer(f,lineterminator='\n')
        fcsv.writerow(list)
        f.flush()
        f.close()



print(jscontents)

#PART 3 遍历，取值
for jscontent in jscontents:

    title = jscontent['title']
    contentUrl=jscontent['docurl']

    if len(jscontent['keywords'])>=2:
        keywords1 =jscontent['keywords'][0]['keyname']
        keywords2 =jscontent['keywords'][1]['keyname']
    else:
        keywords1 = jscontent['keywords'][0]
        keywords2 = 'Technology'
    keywords3 =jscontent['label']

    detailContentObj = detailPage(contentUrl)
    print(n,contentUrl)
    finallist = getuseinfo(detailContentObj,n,keywords1,keywords2,keywords3,title)
    n+=1

    print(n, contentUrl)

