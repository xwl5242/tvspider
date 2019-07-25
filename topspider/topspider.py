#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import time
import uuid
from config import config
import random
import requests
from lxml import etree
from db.mysqldb import DB
"""
banner
https://v.qq.com/
//div[starts-with(@class,'site_slider ')]/div[2]//a/span/text()
//div[starts-with(@class,'site_slider ')]/div[2]//a/@data-bgimage

top
电视剧
https://v.qq.com/channel/tv
电影和纪录片
https://v.qq.com/channel/movie
https://v.qq.com/channel/doco
综艺
https://v.qq.com/channel/variety
动漫和少儿
https://v.qq.com/channel/cartoon
https://v.qq.com/channel/child
"""


class TopSpider:

    def __init__(self):
        self.db = DB()
        self.tv_type_url_map = {'mv': ['https://v.qq.com/channel/movie', 'https://v.qq.com/channel/doco'],
                                'dsj': ['https://v.qq.com/channel/tv'],
                                'zy': ['https://v.qq.com/channel/variety'],
                                'dm': ['https://v.qq.com/channel/cartoon', 'https://v.qq.com/channel/child'],
                                'banner': ['https://v.qq.com']}
        self.tops = []

    def parse_top(self, html):
        if html and isinstance(html, str):
            root = etree.HTML(html)
            name = root.xpath("//div[starts-with(@class,'site_slider ')]/div[2]//a/span/text()")
            img = root.xpath("//div[starts-with(@class,'site_slider ')]/div[2]//a/@data-bgimage")
            self.tops = [(n, img[i]) for (i, n) in enumerate(name)]

    def fetch_top(self, tv_type):
        try:
            url = self.tv_type_url_map.get(tv_type, '')
            if url and len(url) > 0:
                self.db.delete_by_tv_type('t_tv_banner_top', tv_type)
                for u in url:
                    r = requests.get(u, headers={'User-Agent': random.choice(config.UAS)})
                    self.parse_top(r.content.decode('utf-8'))
                    if self.tops and len(self.tops) > 0:
                        for top in self.tops:
                            if top[0] != '大家在看':
                                tv_banner = dict()
                                tv_banner['id'] = str(uuid.uuid4())
                                tv_banner['tv_type'] = tv_type
                                tv_banner['tv_name'] = top[0]
                                tv_banner['tv_img'] = top[1]
                                self.db.insert('t_tv_banner_top', tv_banner)
        except Exception as e:
            print(repr(e))


if __name__ == '__main__':
    ts = TopSpider()
    ts.fetch_top('banner')
    time.sleep(1)
    ts.fetch_top('mv')
    time.sleep(1)
    ts.fetch_top('dsj')
    time.sleep(1)
    ts.fetch_top('dm')
    time.sleep(1)
    ts.fetch_top('zy')

