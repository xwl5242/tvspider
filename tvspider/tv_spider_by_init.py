#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
from config import config
from db.log import logging
from tvspider.save2db import CSV2MD
from tvspider.tv_spider_base import TVSpiderBase as TB


class TVInitSpider(TB):

    def __init__(self, sp, ep):
        self.sp = sp
        self.ep = ep

    def __init_url(self):
        """
        :param s:
        :param e:
        :return:
        """
        web_index_url = [f'{config.TV_SOURCE_URL_BY}?m=vod-index-pg-{i}.html' for i in range(self.sp, self.ep)]
        self.batch_(web_index_url, self.fetch_html, self.parse_index_by_html)

    def detail(self):
        try:
            logging.info(f'fetch tv detail init start...')
            self.__init_url()
            urls = [f'{config.TV_SOURCE_URL_BY}{u[1:]}' for u in self.WEB_INDEX_URL_LIST]
            self.batch_(urls, self.fetch_html, self.parse_detail_by_html)
            logging.info(f'fetch tv detail init end...')
        except Exception as e:
            logging.error(repr(e))


if __name__ == '__main__':
    pass
    # tv_init = TVInitSpider(2, 657)
    # tv_init.detail()
    cm = CSV2MD()
    cm.save_init('1')


