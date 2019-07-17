#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import time
from db.log import logging
from tvspider.cvs2mongodb import CSV2MD
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
        web_index_url = [f'{self.web_root}?m=vod-index-pg-{i}.html' for i in range(self.sp, self.ep)]
        # web_index_url.insert(0, self.web_root)
        self.batch_(web_index_url, self.fetch_html, self.parse_index_html)

    def detail(self):
        try:
            logging.info(f'fetch tv detail init start...')
            self.__init_url()
            urls = [f'{self.web_root}{u[1:]}' for u in self.WEB_INDEX_URL_LIST]
            self.batch_(urls, self.fetch_html, self.parse_detail_html)
            logging.info(f'fetch tv detail init end...')
        except Exception as e:
            logging.error(repr(e))


if __name__ == '__main__':
    pass
    # tv_init = TVInitSpider(2, 650)
    # tv_init.detail()
    # time.sleep(2)
    # cm = CSV2MD()
    # cm.save_init()


