# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from . import items


class CommodityPipeline(object):
    commodity_insert_sql = "INSERT INTO out_restaurant.elm_commodity(c_restaurant_id,c_classify,c_description,c_name,c_foods,c_rating,c_virtual_food_id, \
                 c_image_path,c_tips,c_month_sales,c_food_name,dt_createtime) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now())"

    def open_spider(self, spider):
        import pymysql
        simple_conn_pool = pymysql.Connect(minconn=1, maxconn=1, database="corpus", user="corpus",
                                           password="123456", host="172.18.10.63", port="5432")
        self.conn = simple_conn_pool.getconn()
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if item and isinstance(item, items.ElmCommodityItem):
            try:
                self.cursor.execute(self.commodity_insert_sql,
                                    (item['restaurant_id'], item['classify'], item['description'], item['name'],
                                     item['foods'],
                                     item['rating'], item['virtual_food_id'], item['image_path'],
                                     item['tips'], item['month_sales'], item['food_name']))
            except Exception as e:
                print('保存出错', e)


class ElmRestaurantPipline(object):
    insert_sql = "INSERT INTO out_restaurant.elm_restaurant(c_restaurant_json,c_authentic_id,c_id,c_restaurant_name, c_restaurant_address, c_flavors_name, c_open_hours, c_phone, \
                 c_description,n_rating,c_promotion_info,c_activities_description,c_piecewise_agent_free,n_order_lead_time,n_distance,c_business_name,\
                 c_business_address,n_restaurant_count,dt_createtime) VALUES(%s,%s,%s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,now())"

    def open_spider(self, spider):
        import pymysql
        simple_conn_pool = pymysql.Connect(minconn=1, maxconn=1, database="corpus", user="corpus",
                                           password="123456", host="172.18.10.63", port="5432")
        self.conn = simple_conn_pool.getconn()
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        if item and isinstance(item, items.ElmRestaurantItem):
            try:
                self.cursor.execute(self.insert_sql,
                                    (item['restaurant_json'], item['authentic_id'], item['id'], item['restaurant_name'],
                                     item['restaurant_address'], item['flavors_name'], item['open_hours'],
                                     item['phone'],
                                     item['description'], item['rating'], item['promotion_info'],
                                     item['activities_description'], item['piecewise_agent_free'],
                                     item['order_lead_time'], item['distance'], item['business_name'],
                                     item['business_address'], item['restaurant_count']))
            except Exception as e:
                print('保存出错', e)
