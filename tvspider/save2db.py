#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import json
import uuid
from db.mysqldb import DB
from db.log import logging
from concurrent.futures import ThreadPoolExecutor


class CSV2MD:

    def __init__(self):
        self.db = DB()

    @staticmethod
    def __build_tv(tv_json):
        try:
            tv_o = {}
            tv_json = dict(tv_json)
            for k in tv_json.keys():
                if k != 'urls':
                    tv_o[k] = tv_json.get(k)
            tv_o['img_save'] = '0'
            return tv_o
        except Exception as e:
            logging.error(repr(e))

    @staticmethod
    def __build_urls(tv_id, url_list):
        try:
            u_list = []
            if url_list and len(url_list) > 0:
                for u in url_list:
                    tv_url = dict()
                    tv_url['id'] = str(uuid.uuid4())
                    tv_url['tv_id'] = tv_id
                    tv_url['tv_url'] = str(u).replace(' ', '')
                    u_list.append(tv_url)
            return u_list
        except Exception as e:
            logging.error(repr(e))

    def insert_tv(self, tv):
        """
        :param tv:
        :return:
        """
        try:
            tv_json = dict(json.loads(tv))
            urls = list(tv_json.get('urls', []))
            urls = [u for u in urls if u != ' ' and u != '\t']
            to = CSV2MD.__build_tv(tv_json)
            uo = CSV2MD.__build_urls(tv_json.get('tv_id'), urls)
            self.db.insert_tv(to)
            if uo and len(uo) > 0:
                self.db.insert_urls(uo)
        except Exception as e:
            logging.error(e)

    def save_init(self):
        """
        :return:
        """
        with open('urls.txt', 'r', encoding='GB18030') as ff:
            tvs = ff.readlines()
        logging.info(f'read init csv tv_url data record:{len(tvs)}')
        logging.info('start save init csv data to mongodb')
        try:
            with ThreadPoolExecutor() as e:
                e.map(self.insert_tv, tvs)
        except Exception as e:
            logging.error(e)
        logging.info('end save init csv data to mongodb')

    def save_timing(self):
        with open('urls.txt', 'r', encoding='GB18030') as ff:
            tvs = ff.readlines()
        logging.info(f'read timing csv url data record:{len(tvs)}')
        logging.info('start save timing csv data to mongodb')
        try:
            if tvs and len(tvs) > 0:
                for tv in tvs:
                    tv = dict(json.loads(tv))
                    tv_name = tv.get('tv_name')
                    m_tv = self.db.find_tv_by_name(tv_name)
                    if m_tv:
                        # 已存在
                        tv_id = m_tv.get('tv_id')
                        self.db.update_tv(tv_id, tv.get('update_time'))
                    else:
                        # 不存在
                        tv_id = tv.get('tv_id')
                        self.db.insert_tv(CSV2MD.__build_tv(tv))
                    self.db.delete_tv_urls(tv_id)
                    urls = list(tv.get('urls'))
                    urls = [u for u in urls if u != ' ' and u != '\t']
                    u_list = []
                    for u in urls:
                        u_list.append({'id': str(uuid.uuid4()), 'tv_id': tv_id, 'tv_url': str(u).replace(' ', '')})
                    self.db.insert_urls(u_list)
        except Exception as e:
            logging.error(e)
        logging.info('end save timing csv data to mongodb')

