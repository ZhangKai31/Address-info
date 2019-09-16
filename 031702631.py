#coding = utf-8
import re
import json
import requests
from lxml import etree

url = "https://restapi.amap.com/v3/geocode/geo?output=XML"
input_str = input()
#input_str = "小陈,广东省东莞市凤岗13965231525镇凤平路13号"
#http = 0,地址完整；http = 1,调用API补齐地址
http = 0

name = re.match(r'(.+)(?=,)',input_str).group()
phone = re.search(r'\d{11,}',input_str).group()
add = re.findall(r'(?<=,).+',input_str)
#print(name)
#print(phone)
addr = add[0].replace(phone,"")
#print(addr)

#检查group()是否可能None
province = re.match(r'.+省',addr)
if province == None:
    province = re.match(r'(.+?)(?=市)',addr)
    if province == None:
        http = 1
    else:
        province = province.group()
    if province == "北京" or province == "天津" or province == "重庆" or province == "上海":
        province = province
    else:
        http = 1
else:
    province = province.group()


city = re.search(r'(?<=省)(.+)市',addr)
if city == None:
    city = re.match(r'(.+?)(?<=市)',addr)
    if city == None:
        http = 1                                                    #不考虑直辖县，若没有市级，则地址不完整
    else:
        city = city.groups()[0]
else:
    city = city.group()

district = re.search(r'(?<=市)(.+?)(?<=[区县])',addr)
if district == None:
    district = ""
else:
    district = district.groups()[0]

street = re.search(r'(?<=[县区])(.+)[镇乡]',addr)
if street == None:
    street = re.search(r'(?<=[县区])(.+)[街][道]', addr)
    if street == None:
        street = re.search(r'(?<=[市])(.+)[镇乡]', addr)
        if street == None:
            street = re.search(r'(?<=[市])(.+)[街][道]', addr)
            if street == None:
                street = ""
            else:
                street = street.group()
        else:
            street = street.group()
    else:
        street = street.group()
else:
    street = street.group()


home = re.search(r'(?<=[镇乡])(.+)',addr)  #街后
if home == None:
    home = re.search(r'(?<=[街][道])(.+)',addr)
    if home == None:
        home = re.search(r'(?<=[区县]).+',addr)
        if home == None:
            home = re.search(r'(?<=[市]).+',addr).group()                #home一定不为None;若无匹配的home,默认市级后面的地址是home
        else:
            home = home.group()
    else:
        home = home.group()
else:
    home = home.group()

if http == 1:
    params = {
        "address": addr,
        "key": "dda771403ae1b26d2a822e95f4dd2327"
    }
    response = requests.get(url, params=params)
    position = response.text
    e = etree.HTML(position.encode())
    province = e.xpath('//province/text()')
 #   print(province[0])
    city = e.xpath('//city/text()')
#  print(city[0])
    district = e.xpath('//district/text()')
#    print(district[0])
#else:
#   print(province)
#    print(city)
#    print(district)

#print(street)

#对具体位置home继续细分
#print("------------home-------------")
#print(home)
res = 0

road = re.search(r'(.+?)(?<=[路街巷])',home)
if(road == None):
    road = ""
else:
    road = road.group()
    res += 1

num =re.search(r'\d+号',home)
if num == None:
    num = ""
else:
    num = num.group()
    res +=1

location = re.search(r'(?<=号).+',home)
if location == None:
    #location = re.search(r'(?<=[路街巷]).+',home)
    if res == 0:
        location = home
    else:
        location = ""
else:
    location = location.group()

#print(type(province))
#print(type(location))
if type(province) == list:
    province = str(province[0])
if type(city) == list:
    city = str(city[0])
if type(district) == list:
    district = str(district[0])
if type(street) == list:
    street = str(street[0])

info = {
    "姓名":name,
    "手机":phone,
    "地址":[province,city,district,street,road,num,location]
}
json_info = json.dumps(info,ensure_ascii=False)

print(json_info)


