#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import time
import random
import requests
from lxml import etree
from db.log import logging
from config import config
from tvspider.save2db import CSV2MD
from tvspider.tv_spider_base import TVSpiderBase as TB


class TVSpiderTiming(TB):

    def __init__(self, ft):
        super(TVSpiderTiming, self).__init__(ft)
        self.ft = ft
        self.timing_file = config.TV_FS_TIMIMG_FILE_MAP.get(ft)
        self.CUR_2_LAST_URLS = []
        self.CUR_2_LAST_PAGE = 1
        self.__read_last_fetch_time()
        self.__flush_urls_file()

    def __flush_urls_file(self):
        sf = open(self.urls_file, 'w')
        sf.write('')
        sf.close()

    def __read_last_fetch_time(self):
        f = open(self.timing_file, 'r')
        self.timing = f.read()
        f.close()

    @staticmethod
    def __date_str_compare(date_str_1, date_str_2):
        """
        :param date_str_1:
        :param date_str_2:
        :return:
        """
        date_str_1 = time.mktime(time.strptime(date_str_1, '%Y-%m-%d %H:%M:%S'))
        date_str_2 = time.mktime(time.strptime(date_str_2, '%Y-%m-%d %H:%M:%S'))
        return int(date_str_1) - int(date_str_2)

    def __timing_url(self, web_root):
        """
        :return:
        """
        logging.info(f'fetch tv {self.ft} index url timing start...')
        r = requests.get(web_root, headers={'User-Agent': random.choice(config.UAS)})
        index_url = etree.HTML(r.text).xpath(config.TV_FS_XPATH_MAP.get(self.ft).get('tv_index_url_xpath'))
        times = etree.HTML(r.text).xpath(config.TV_FS_XPATH_MAP.get(self.ft).get('tv_index_fetch_date_xpath'))
        i = 0
        for n, ti in enumerate(times):
            ti = str(ti).strip()
            if self.__date_str_compare(ti, self.timing) > 0:
                self.CUR_2_LAST_URLS.append(index_url[n])
                self.WEB_INDEX_URL_TIME_MAP[index_url[n][1:]] = ti
                i += 1
            else:
                break
        if i == len(times):
            self.CUR_2_LAST_PAGE += 1
            self.__timing_url(f'{self.web_root}?m=vod-index-pg-{self.CUR_2_LAST_PAGE}.html')
        logging.info(f'fetch tv {self.ft} index url timing end...')

    def detail(self):
        try:
            logging.info(f'fetch tv {self.ft} detail timing start...')
            # 修改采集时间
            with open(self.timing_file, 'w') as fff:
                fff.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            # 采集视频index url
            self.__timing_url(self.web_root)
            # 开始采集detail
            urls = [f'{self.web_root}{u[1:]}' for u in self.CUR_2_LAST_URLS]
            self.batch_(urls, self.fetch_html, self.parse_detail_html)
            logging.info(f'fetch tv {self.ft} detail timing end...')
        except Exception as e:
            # 异常，采集时间回滚到之前
            with open(self.timing_file, 'w') as fff:
                fff.write(self.timing)
            logging.error(repr(e))


def main(ft):
    tt = TVSpiderTiming(ft)
    tt.detail()
    cm = CSV2MD(ft)
    cm.save_timing()


if __name__ == '__main__':
    main(config.TV_TYPE_MAIN)
    main(config.TV_TYPE_3PART)


