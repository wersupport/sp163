# kingxuan  GQdM saRU 6Crh kkSY zAF7 vzHl application psd

import os
import requests
import json

path = os.path.abspath(os.path.dirname(__file__))


user_id = 'kingxuan'
user_password = 'GQdM saRU 6Crh kkSY zAF7 vzHl'
end_point_url_img = 'https://wersupport.com/wp-json/wp/v2/media'

title = 'rest api title'
status = 'publish'
author = '1'
content = 'test content'
featureimg1=path+'/1天猫-网店.png'
featureimg=featureimg1.encode('utf8')
print(featureimg)

featureimgname, featureimgextention = os.path.splitext(featureimg)

#if featureimgextention =='png':
contentimg = 'image/png'


headers = {'Content-Type': contentimg,'Content-Disposition':'attahment; filename=%s' %featureimg}

post = {
        'caption': '1234',
        'description':'5678'
}

data = open(featureimg, 'rb').read()

response = requests.post(url=end_point_url_img, data=data,headers=headers, json=post,auth=(user_id,user_password))
print(response)