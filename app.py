#!/usr/bin/env python
#-*-coding:u8

import tornado.ioloop
import tornado.web
import time
from tornado.options import options
import os
import torndb
import json
import decimal
import sys
import importlib
from config import dbs

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)

def jd(data):
    return json.dumps(data, ensure_ascii=False, default=decimal_default)

def date_format(timestamp):
    _format = "%Y-%m-%d %H:%M:%S.%s"
    ltime=time.localtime(timestamp)
    return time.strftime(_format, ltime)

def _log(handler):
    """
    GET show/search?search=haha&name=11
    query search=haha&name=11
    query_arguments {'search': ['haha'], 'name': ['11']}
 
    POST show/search
    Content-Type application/json
    
    body {"gsv":"4.4.4","uid":"3314310","os":"android","ts":"2016-04-20 08:06:15","events":[{"category":"裙子","pv_num":"566","position":"-1","tab_2":"品类","ts":"2016-04-20 03:28:10","tab_1":"category","tab_3":"裙子","eventname":"tab3_c"}
    ],"push_token":"GT;;d550c23a579ea97332038ea10629ad2a","isp":"tel","appkey":"mxyc","gc":"tengxun","gf":"android","net":"wifi","ip":"","duration":"154","gi":"b2b91ca6-f52e-43af-a5e5-d86467235f84","gv":"6.6.0","gt":"HUAWEI C199s by huanglei","gs":"720x1184","access_token":"jtbYfjVA9A4Ype5tK2rN4C8Kge7lXvY7kePxO0q5gCQ"}
    """

    r = handler.request
    request_time = 1000.0 * r.request_time()
    print  r.remote_ip, date_format(r._start_time), handler.get_status(), r.path, request_time, r.headers.get("User-Agent"), r.query, r.query_arguments, r.body, {k:v for (k, v) in r.headers.get_all()}

settings = dict(
    #cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    #login_url= "/login",
    #xsrf_cookies= True,
    debug = True,
    log_function = _log
)

"""
查询方式分为两个方式， 一个是get 一个post
"""
class MainHandler(tornado.web.RequestHandler):
    """
    首页
    """
    def get(self):
        inf = {
            "show": "http://127.0.0.1:8888/show/shop/brand_info?__ecs_business_info__business_id=1",
            "show_bulk": "http://127.0.0.1:8888/show/shop/brand_info?__ecs_business_info__business_id__in=1,2,3",
            "info": "http://127.0.0.1:8888/inf/shop/brand_info?__ecs_business_info__business_id__neq=1",
            "info_bulk": "http://127.0.0.1:8888/inf/shop/brand_info?__ecs_business_info__business_id__not_in=1,2,3",
            "struct": "http://127.0.0.1:8888/struct/shop/?search=common.categories_v2.cid",
            "struct2": "http://127.0.0.1:8888/struct/shop/all?search=common.categories_v2.cid&search=common.categories_v2.name"
        }
        i = []
        for key in inf:
            i.append("<a href='%s'>%s : %s</a>" % (inf[key], key, inf[key]))
        self.write("<hr>".join(i))

def get_engine(db_name):
    info = dbs.get(db_name)
    engine_type = info.get("type", "mysql")
    module = importlib.import_module("plugin."+ engine_type + "_plugin")
    return module.Engine(db_name, **info)

class ShowHandler(tornado.web.RequestHandler):
    """
    显示接口查询语句
    """
    def get(self, db_name, inf_name):
        
        self.write(get_engine(db_name).show(inf_name, self.request))

class InfHandler(tornado.web.RequestHandler):
    """
    查询数据
    """
    def get(self, db_name, inf_name):
        engine = get_engine(db_name)
        res = engine.search(inf_name, self.request)
        self.write(jd(res))

class StructHandler(tornado.web.RequestHandler):
    """
    获得某个数据库某个表中字段的类型
    """
    def get(self, db_name, show_type=None):
        """
        show FULL COLUMNS from shop.ecs_business_info where Field="business_id"
        """
        engine = get_engine(db_name)
        res = engine.struct(show_type, self.request)
        self.write(jd(res))

class DebugHandler(tornado.web.RequestHandler):
    """
    """
    def get(self, db_name, inf_name):
        self.write(get_engine(db_name).debug(inf_name, self.request))


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/show/(.*)/(.*)", ShowHandler),
    (r"/inf/(.*)/(.*)", InfHandler),
    (r"/struct/(.*)/(.*)", StructHandler),
    (r"/debug/(.*)/(.*)", DebugHandler),
], **settings)

if __name__ == "__main__":
    #print get_conn("shop")
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
