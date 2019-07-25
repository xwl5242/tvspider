#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import time
from config import config
from db.log import logging
from tvspider.save2db import CSV2MD
from tvspider.tv_spider_base import TVSpiderBase as TB


class TVInitSpider(TB):

    def __init__(self, ft, sp, ep):
        self.ft = ft
        self.sp = sp
        self.ep = ep
        super(TVInitSpider, self).__init__(ft)

    def __init_url(self):
        """
        :return:
        """
        logging.info(f'fetch tv {self.ft} index url start...')
        web_index_url = [f'{self.web_root}?m=vod-index-pg-{i}.html' for i in range(self.sp, self.ep)]
        self.batch_(web_index_url, self.fetch_html, self.parse_index_html)
        logging.info(f'fetch tv {self.ft} index url end...')

    def detail(self):
        try:
            logging.info(f'fetch tv {self.ft} detail init start...')
            self.__init_url()
            urls = [f'{self.web_root}{u[1:]}' for u in self.WEB_INDEX_URL_LIST]
            self.batch_(urls, self.fetch_html, self.parse_detail_html)
            logging.info(f'fetch tv {self.ft} detail init end...')
        except Exception as e:
            logging.error(repr(e))


def main(ft, s, e):
    tv_init = TVInitSpider(ft, s, e)
    tv_init.detail()
    # time.sleep(1)
    # cm = CSV2MD(ft)
    # cm.save_init()


if __name__ == '__main__':
    main(config.TV_TYPE_MAIN, 2, 658)
    main(config.TV_TYPE_BACKUP, 2, 438)
    main(config.TV_TYPE_3PART, 2, 850)
