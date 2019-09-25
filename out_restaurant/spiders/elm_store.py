import scrapy
import json
import random
import Geohash
from ..items import ElmRestaurantItem
from .. import settings

#城市地址
CITIES_URL="https://www.ele.me/restapi/shopping/v1/cities"
# 商圈地址
BUSINESS_URL = "https://www.ele.me/restapi/v2/pois?extras[]=count&geohash=${geohash}&type=nearby"
# 店铺地址
RESTAURANT_URL = "https://www.ele.me/restapi/shopping/restaurants?extras[]=activities&geohash=${geohash}&latitude=${latitude}&longitude=${longitude}&offset=${offset}&terminal=web"

class ElmRestaurant(scrapy.Spider):
    name = "elmrestaurant"
    # 种子用户
    initial_users = ['189610768']
    cookie = "ubt_ssid=ys866tuqh449bwl2mxkdgxxpr6r16le8_2018-02-07; _utrace=70249066d5184d1cdf43a5f0c6b3158f_2018-02-07; track_id=1517980339%7Cfe3f612411306edc3a60f71d10648f2011b85ff26b716ac130%7C8924a7f4e011ab3db702bb851250463a; eleme__ele_me=457bb522b5b1e167ff026a5f283d3bcc%3A045750f2bad532b5fd8f81a4af74d433b09c3720; perf_ssid=sbmhl7jh57khxdy7h7e76t3tl3xvn9jp_2018-02-07; " \
             "IM_USER_SOURCE=eleme-pc; IM_CUSTOMER_TOKEN=65e89e5c4cb3e043551a494b55eaa358;USERID=${userId}"
    # 引用地址
    referer = "Referer: https://www.ele.me/place/${geohash}?latitude=${latitude}&longitude=${longitude}"
    handle_httpstatus_list = [401,403,430]

    def start_requests(self):
        #获取全国城市的经纬度
        print("开始：获取全国各城市的经纬度")
        yield scrapy.Request(url=CITIES_URL,callback=self.parse_cities_geohash)

    def parse_cities_geohash(self,response):
        json_cities = json.loads(response.text)
        for json_key in json_cities.keys():
            for json_data in json_cities.get(json_key):
                #将每个城市的经纬度转化成geohash
                geohash = Geohash.encode(json_data.get("latitude"),json_data.get("longitude"),12)
                print("开始下一地区：%s 的爬取 " % json_data.get("name"))
                yield scrapy.Request(url=BUSINESS_URL.replace('${geohash}', geohash),
                                     headers={'user-agent': random.choice(settings.USER_AGENT_LIST)},callback=self.parse_business)

    def parse_business(self,response):
        json_list = json.loads(response.text)
        Cookie = self.cookie.replace('${userId}', random.choice(self.initial_users))
        offset=24
        #遍历商圈集合
        for json_data in json_list:
            latitude=json_data.get("latitude")#纬度
            longitude=json_data.get("longitude")#经度
            geohash=json_data.get("geohash")#地区hash
            restaurant_url = RESTAURANT_URL.replace('${geohash}', geohash).replace('${latitude}', str(latitude)).replace(
                '${longitude}', str(longitude))
            # 每次请求根据经纬度构造referer
            Referer = self.referer.replace('${geohash}',str(geohash)).replace('${latitude}', str(latitude)).replace('${longitude}', str(longitude))
            print("经度：%s,纬度：%s\n 地区hash:%s\n 商铺请求地址：%s\n" % (longitude,latitude,geohash,restaurant_url.replace('${offset}', str(offset))))
            yield scrapy.Request(url=restaurant_url.replace('${offset}', str(offset)),callback=self.restaurant_item,
                                 headers={'Cookie':Cookie,'Referer':Referer},
                                 meta={"business_json":json_data,'restaurant_url':restaurant_url,'offset':str(offset),
                                       'Referer':Referer})

    def restaurant_item(self,response):
        item=ElmRestaurantItem()
        Cookie = self.cookie.replace('${userId}', random.choice(self.initial_users))
        business_json=response.meta.get("business_json")
        if response.status >= 200 and response.status <= 300:
           restaurant_json_list=json.loads(response.text)
        for restaurant_json in restaurant_json_list:
            item['business_name']=business_json.get("name")
            item['business_address']=business_json.get("address")
            item['restaurant_count']=business_json.get("count")
            item['authentic_id'] = restaurant_json.get("authentic_id")
            item['id'] = restaurant_json.get("id")
            item['restaurant_name']=restaurant_json.get("name")
            item['restaurant_address'] = restaurant_json.get("address")
            item['open_hours'] = restaurant_json.get("opening_hours")
            item['phone'] = restaurant_json.get("phone")
            item['description'] = restaurant_json.get("description")
            item['rating'] = restaurant_json.get("rating")
            item['promotion_info'] = restaurant_json.get("promotion_info")
            piecewise=restaurant_json.get("piecewise_agent_free")
            if piecewise:
               item['piecewise_agent_free'] = piecewise.get("description")
            else:
                item['piecewise_agent_free'] = ''
            item['order_lead_time'] = restaurant_json.get("order_lead_time")
            item['distance'] = restaurant_json.get("distance")
            #对商家经营种类进行分割
            fla_info = []
            flav =restaurant_json.get("flavors")
            if flav:
               for flavors in flav:
                   fla_info.append("{0}".format(flavors.get("name")))
               item['flavors_name'] = '&'.join(fla_info)
            else:
                item['flavors_name'] = ''
            #对商家活动进行拼接 iconname_name_description
            act_dec=[]
            for activities_description in restaurant_json.get("activities"):
                act_dec.append("{0}:{1};{2};".format(activities_description.get("icon_name"),activities_description.get("name"),activities_description.get("description")))
            item['activities_description'] = '\n'.join(act_dec)
            item['restaurant_json'] = json.dumps(restaurant_json)
            yield item
        # offset偏移量每次增加24
        offset = int(response.meta.get("offset"))
        print("%s:第%s次请求数据\n" % (str(business_json.get("name")),str(offset / 24)))
        if response.text != "[]":
            restaurant_url=str(response.meta.get("restaurant_url"))
            offset =int(response.meta.get("offset")) + 24
            yield scrapy.Request(url=restaurant_url.replace('${offset}',str(offset)),
                                 callback=self.restaurant_item,
                                 headers={'Cookie': Cookie,'Referer': response.meta.get("Referer")},
                                 meta={'business_json': business_json,'offset':str(offset),'restaurant_url':restaurant_url})
