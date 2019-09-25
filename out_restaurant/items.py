# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OutRestaurantItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class ElmRestaurantItem(scrapy.Item):
    restaurant_name = scrapy.Field() #店铺名称
    restaurant_address = scrapy.Field()#店铺地址
    flavors_name = scrapy.Field()#风味名称
    open_hours = scrapy.Field()#营业时间
    phone = scrapy.Field()#订餐电话
    description = scrapy.Field()#描述
    rating = scrapy.Field()  # 评价
    promotion_info=scrapy.Field()#优惠信息
    activities_description = scrapy.Field()#店铺活动描述
    piecewise_agent_free = scrapy.Field()#地段配送信息
    order_lead_time = scrapy.Field()#平均送到时间
    distance = scrapy.Field()#距离
    business_name = scrapy.Field()  # 商圈名称
    business_address = scrapy.Field()  # 商圈地点
    restaurant_count = scrapy.Field()  # 数量
    authentic_id = scrapy.Field() #商铺真实id
    id = scrapy.Field() #商铺id
    restaurant_json = scrapy.Field() #商铺原始数据

class ElmCommodityItem(scrapy.Item):
    classify=scrapy.Field()
    description = scrapy.Field()
    name = scrapy.Field()
    foods = scrapy.Field()
    rating = scrapy.Field()
    virtual_food_id = scrapy.Field()
    restaurant_id = scrapy.Field()
    tips = scrapy.Field()
    month_sales = scrapy.Field()
    food_name = scrapy.Field()
    image_path = scrapy.Field()




