# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from. import settings
import random
import logging
from .rotateproxy import RotateProxy
import time
class RotateUserAgentMiddleware(UserAgentMiddleware):
    """
    动态切换浏览器
    """
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):

        if settings.USER_AGENT_LIST:
            user_agen = random.choice(settings.USER_AGENT_LIST)
            if user_agen:
                request.headers.setdefault('User-Agent', user_agen)

class RotateProxyMiddleware(object):
    """
    动态切换ip代理
    """
    def __init__(self):
        # Create and launch a thread
        if settings.IP_PROXY_ENABLE:
            from threading import Thread
            self.ip_proxy = settings.IP_PROXY_CONFIG
            self.proxy_list = RotateProxy.init()
            t=Thread(target=self.get_proxy_task)
            t.setDaemon(True)
            t.start()

    def process_request(self, request, spider):
        if settings.IP_PROXY_ENABLE:
            self.proxy_list=RotateProxy.judgeProxy(200,'')
            print("代理ip集合为:%s" % self.proxy_list)
            if  self.proxy_list:
                proxy_ip = 'https://%s' % (random.choice(self.proxy_list))
                print('代理动态选取: %s' % proxy_ip)
                request.meta['proxy'] = proxy_ip
            else:  # 如果代理池为空，则每个请求延迟0.5秒，防止ip被ban
                time.sleep(0.5)
                logging.INFO('未获取可用代理')

    def get_proxy_task(self):
        while True:
            time.sleep(self.ip_proxy.get('FETCH_INTERVAL', 5) * 60)
            self.proxy_list = RotateProxy.init()
            logging.info('获取ip代理池成功')




class OutRestaurantSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        if response.status >=400 and response.status<= 430:
            proxy_ip = response.meta['proxy']
            print("返回状态%s的ip:%s" %(response.status,proxy_ip))
            RotateProxy.judgeProxy(response.status, proxy_ip)
        return

    # def process_spider_output(response, result, spider):
    #     # Called with the results returned from the Spider, after
    #     # it has processed the response.
    #
    #     # Must return an iterable of Request, dict or Item objects.
    #     for i in result:
    #         yield i
    # def process_spider_exception(response, exception, spider):
    #     # Called when a spider or process_spider_input() method
    #     # (from other spider middleware) raises an exception.
    #
    #     # Should return either None or an iterable of Response, dict
    #     # or Item objects.
    #     pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
