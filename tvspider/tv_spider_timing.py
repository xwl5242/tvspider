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

    def __init__(self):
        f = open('timing.txt', 'r')
        self.timing = f.read()
        self.CUR_2_LAST_URLS = []
        self.CUR_2_LAST_PAGE = 1

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

    def __timing_url(self, web_index_url, ft):
        """
        :return:
        """
        r = requests.get(web_index_url, headers={'User-Agent': random.choice(config.UAS)})
        if ft == '0':
            index_url = etree.HTML(r.text).xpath("//tr[@class='row']/td[position()=1]/a/@href")
            times = etree.HTML(r.text).xpath("//tr[@class='row']/td[position()=4]/font//text()")
        else:
            index_url = etree.HTML(r.text).xpath("//span[@class='xing_vb4']/a/@href")
            times = etree.HTML(r.text).xpath("//span[@class ='xing_vb7']/text()")
        i = 0
        for n, ti in enumerate(times):
            if self.__date_str_compare(ti, self.timing) > 0:
                self.CUR_2_LAST_URLS.append(index_url[n])
                self.WEB_INDEX_URL_TIME_MAP[index_url[n][1:]] = ti
                i += 1
            else:
                break
        if i == len(times):
            self.CUR_2_LAST_PAGE += 1
            self.__timing_url(f'{self.web_root if ft == "0" else config.TV_SOURCE_URL_BY}?m=vod-index-pg-'
                              f'{self.CUR_2_LAST_PAGE}.html')

    def detail(self, ft):
        try:
            logging.info(f'fetch tv detail timing start...')
            timing_file = 'timing.txt' if ft == '0' else 'timing_by.txt'
            with open(timing_file, 'w') as fff:
                fff.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            self.__timing_url(self.web_root if ft == '0' else config.TV_SOURCE_URL_BY)
            urls = [f'{self.web_root}{u[1:]}' for u in self.CUR_2_LAST_URLS]
            self.batch_(urls, self.fetch_html, self.parse_detail_html if ft == '0' else self.parse_detail_by_html())
            logging.info(f'fetch tv detail timing end...')
        except Exception as e:
            timing_file = 'timing.txt' if ft == '0' else 'timing_by.txt'
            with open(timing_file, 'w') as fff:
                fff.write(self.timing)
            logging.error(repr(e))


def main(ft):
    urls_file = 'urls.txt' if ft == '0' else 'urls_by.txt'
    sf = open(urls_file, 'w')
    sf.write('')
    sf.close()
    tt = TVSpiderTiming()
    tt.detail(ft)
    time.sleep(1)
    cm = CSV2MD()
    cm.save_timing(ft)


if __name__ == '__main__':
    main('0')
    main('1')


