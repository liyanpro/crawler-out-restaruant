import PyMySQL
import pymysql
import scrapy
import json
from ..items import ElmCommodityItem

#商品地址
COMMODITY_URL = "https://www.ele.me/restapi/shopping/v2/menu?restaurant_id=${id}"
#图片地址
IMAGE_PATH="http://fuss10.elemecdn.com/${hash_path}.jpeg"
class ElmCommodity(scrapy.Spider):
    name = "elmcommodity"
    handle_httpstatus_list = [401,403,430]
    #先按照时间段进行查询，等爬取所有商铺后在查询大于此时间的所有商铺商品
    select_sql = "select DISTINCT c_id from out_restaurant.restaurant_copy where dt_createtime < TIMESTAMP '2018-02-28 16:20:31.31422' order by c_id asc "
    def start_requests(self):
        #获取商铺id
        simple_conn=pymysql.Connect(minconn=1, maxconn=1, database="corpus", user="corpus",
                                                              password="123456", host="172.18.10.63", port="5432")
        conn = simple_conn.getconn()
        cursor=conn.cursor()
        cursor.execute(self.select_sql)
        rows=cursor.fetchall()
        cursor.close()
        if rows:
            for row in rows:
                print("开始抓取商铺id：%s 的商品" % (str(row[0])))
                yield scrapy.Request(url=COMMODITY_URL.replace('${id}', str(row[0])),
                                     callback=self.commodity_item)

    def commodity_item(self,response):
        item=ElmCommodityItem()
        commodity_list=[]
        if response.status>=200 and response.status<=300:
            commodity_list=json.loads(response.text)
        for commodity in commodity_list:
            item['classify'] = json.dumps(commodity)
            item['description'] = commodity.get("description")
            item['name']=commodity.get("name")
            foods = commodity.get("foods")
            item['foods']=json.dumps(foods)
            for food in foods:
                item['rating'] = food.get("rating")
                item['virtual_food_id']=food.get("virtual_food_id")
                item['restaurant_id']=food.get("restaurant_id")
                item['tips']=food.get("tips")
                item['month_sales']=food.get("month_sales")
                item['food_name']=food.get("name")
                imagepath=food.get("image_path")
                if imagepath:
                    item['image_path']=IMAGE_PATH.replace('${hash_path}',self.Str_handle(imagepath))
                else:
                    item['image_path']=''
                yield item

    def Str_handle(self,image_path):
        image = list(image_path)
        image.insert(1, '/')
        image.insert(4, '/')
        new_image="".join(image)
        return new_image




