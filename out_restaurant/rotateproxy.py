from. import settings
import requests
import logging
class RotateProxy(object):
     #代理ip集合
     proxy_list=[]
     @classmethod
     def init(cls):
         cls.ip_proxy = settings.IP_PROXY_CONFIG
         cls.proxy_url = cls.ip_proxy['URL'].format(num=cls.ip_proxy['FETCH_NUM'])
         response = requests.get(cls.proxy_url)
         json_data = response.json()
         if not json_data.get('success'):
             logging.warning('获取代理失败: %s' % response.text)
         else:
             ip_list = json_data.get('data')
             cls.proxy_list = ['%s:%s' % (line.get('ip'), line.get('port')) for line in ip_list]
             return cls.proxy_list
     '''
     剔除无效ip，重新从芝麻代理获取有效ip
     '''
     @classmethod
     def getProxy(cls,invaild_ip):
         flag=False
         for ip in cls.proxy_list:
             if  ip in invaild_ip:
                 print("剔除的ip为：%s" % (ip))
                 cls.proxy_list.remove(ip)
                 flag=True
                 break
         if flag:
             cls.proxy_url = cls.ip_proxy['URL'].format(num=1)
             response=requests.get(cls.proxy_url)
             new_data=response.json().get('data')
             #将新ip添加到ip列表的尾部
             print("重新获取ip：%s" % (str(new_data)))
             for new_ip in new_data:
                 cls.proxy_list.append("{0}:{1}".format(new_ip.get('ip'),new_ip.get('port')))
             print("最新ip集合：",cls.proxy_list)
         return cls.proxy_list
     '''
     spider调用的方法，判断当前ip是否可用并返回有效的ip集合
     参数：status为返回的状态码，invaild_ip为失效的ip
     '''
     @classmethod
     def judgeProxy(cls,status,invaild_ip):
         if status>=400 and status<=430:
             return cls.getProxy(invaild_ip)
         else:
             return cls.proxy_list
