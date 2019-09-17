#coding = utf-8
import re
import json
import requests
from lxml import etree

#检查group()是否可能None
def get_province(addr):
    global province
    global http
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
    pass

def get_city(addr):
    global http
    global city
    city = re.search(r'(?<=省)(.+)市',addr)
    if city == None:
        city = re.match(r'(.+?)(?<=市)',addr)
        if city == None:
            http = 1                                                    #不考虑直辖县，若没有市级，则判定地址不完整
        else:
            city = city.groups()[0]
    else:
        city = city.group()
    pass

def get_district(addr):
    global district
    district = re.search(r'(?<=市)(.+?)(?<=[区县])',addr)
    if district == None:
        district = ""
    else:
        district = district.groups()[0]
    pass

def get_street(addr):
    global street
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
    pass

def get_home(addr):
    global home
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
    pass

def HTTPmap(addr):
    global province,city,district
    url = "https://restapi.amap.com/v3/geocode/geo?output=XML"
    params = {
            "address": addr,
            "key": "dda771403ae1b26d2a822e95f4dd2327"
        }
    response = requests.get(url, params=params)
    position = response.text
    e = etree.HTML(position.encode())
    province = e.xpath('//province/text()')
    city = e.xpath('//city/text()')
    district = e.xpath('//district/text()')
    pass



#对具体位置home继续细分
def cut_home(home):
    res = 0
    global road,num,location
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
        if res == 0:
            location = home
        else:
            location = ""
    else:
        location = location.group()
    pass

def main():
    input_str = input()
    # http = 0,地址完整；http = 1,调用API补齐地址
    global province,city,district,street,home,road,num,location,http
    http = 0

    name = re.match(r'(.+)(?=,)', input_str).group()
    phone = re.search(r'\d{11,}', input_str).group()
    add = re.findall(r'(?<=,).+', input_str)
    addr = add[0].replace(phone, "")

    get_province(addr)
    get_city(addr)
    get_district(addr)
    get_street(addr)
    get_home(addr)

    if http == 1:
        HTTPmap(addr)

    cut_home(home)

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
    pass
