#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import json
import uuid
from db.db import DB
from db.log import logging
from concurrent.futures import ThreadPoolExecutor


class CSV2MD:

    def __init__(self):
        self.db = DB()

    @staticmethod
    def __build_tv(tv_json):
        tv_o = {}
        tv_json = dict(tv_json)
        for k in tv_json.keys():
            if k != 'urls1' and k != 'urls2':
                tv_o[k] = tv_json.get(k)
        tv_o['img_save'] = '0'
        return tv_o

    @staticmethod
    def __build_urls(tv_id, tv_source, url_list):
        u_list = []
        if url_list and len(url_list) > 0:
            for u in url_list:
                tv_url = {}
                tv_url['id'] = str(uuid.uuid4())
                tv_url['tv_id'] = tv_id
                tv_url['tv_source'] = tv_source
                tv_url['tv_url'] = str(u).replace(' ', '')
                u_list.append(tv_url)
        return u_list

    def insert_tv(self, tv):
        """
        :param tv:
        :return:
        """
        try:
            tv_json = dict(json.loads(tv))
            urls1 = list(tv_json.get('urls1', []))
            urls2 = list(tv_json.get('urls2', []))
            urls1 = [u for u in urls1 if u != ' ' and u != '\t']
            urls2 = [u for u in urls2 if u != ' ' and u != '\t']
            to = CSV2MD.__build_tv(tv_json)
            uo1 = CSV2MD.__build_urls(tv_json.get('tv_id'), '1', urls1)
            uo2 = CSV2MD.__build_urls(tv_json.get('tv_id'), '2', urls2)
            self.db.insert_one('t_tv', to)
            if uo1 and len(uo1) > 0:
                self.db.insert_many('t_tv_urls', uo1)
            if uo2 and len(uo2) > 0:
                self.db.insert_many('t_tv_urls', uo2)
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
                    m_tv = self.db.find_one('t_tv', {"tv_name": tv_name})
                    if m_tv:
                        # 已存在
                        tv_id = m_tv.get('tv_id')
                        self.db.update('t_tv', {"tv_id": [tv_id, tv_id], "update_time": [m_tv.get('update_time'), tv.get('update_time')]})
                    else:
                        # 不存在
                        self.db.insert_one('t_tv', CSV2MD.__build_tv(tv))

                    urls1 = list(tv.get('urls1'))
                    urls1 = [u for u in urls1 if u != ' ' and u != '\t']
                    urls2 = list(tv.get('urls2'))
                    urls2 = [u for u in urls2 if u != ' ' and u != '\t']
                    c1 = self.db.count('t_tv_urls', {'tv_source': '1', 'tv_id': tv.get('tv_id')})
                    c2 = self.db.count('t_tv_urls', {'tv_source': '2', 'tv_id': tv.get('tv_id')})
                    for u in urls1[c1:]:
                        self.db.insert_one('t_tv_urls', {'id': str(uuid.uuid4()), 'tv_id': tv.get('tv_id'),
                                                         'tv_source': '1', 'tv_url': str(u).replace(' ', '')})
                    for u in urls2[c2:]:
                        self.db.insert_one('t_tv_urls', {'id': str(uuid.uuid4()), 'tv_id': tv.get('tv_id'),
                                                         'tv_source': '2', 'tv_url': str(u).replace(' ', '')})
        except Exception as e:
            import traceback
            traceback.print_exc()
            logging.error(e)
        logging.info('end save timing csv data to mongodb')


