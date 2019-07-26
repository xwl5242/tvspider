#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import json
import uuid
from config import config
from db.mysqldb import DB
from db.log import logging
from concurrent.futures import ThreadPoolExecutor


class CSV2MD:

    def __init__(self, ft):
        self.ft = ft
        self.urls_file = config.TV_FS_FILE_MAP.get(ft)
        self.db = DB()
        self.tv_table_name = {config.TV_TYPE_MAIN: 't_tv', config.TV_TYPE_3PART: 't_tv_3part'}.get(ft)
        self.tv_urls_table_name = {config.TV_TYPE_MAIN: 't_tv_urls', config.TV_TYPE_3PART: 't_tv_urls_3part'}.get(ft)

    @staticmethod
    def __build_tv(tv_json):
        try:
            tv_o = {}
            tv_json = dict(tv_json)
            for k in tv_json.keys():
                if k != 'urls':
                    if k == 'tv_intro':
                        v = tv_json.get(k)
                        v = str(v).replace(' ', '').replace('\t', '')
                        v = v[:2000]+'...' if len(v) > 2000 else v
                    elif k == 'tv_name':
                        v = tv_json.get(k)
                        v = str(v).replace(' ', '').replace('~', '')\
                            .replace('~', '').replace('[T]', '').replace('?', '').replace('？', '').replace('·', '')
                    else:
                        v = tv_json.get(k)
                    tv_o[k] = v
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
        try:
            tv_json = dict(json.loads(tv))
            tv_name = tv_json['tv_name']
            if tv_name:
                urls = list(tv_json.get('urls', []))
                urls = [u for u in urls if u != ' ' and u != '\t']
                to = CSV2MD.__build_tv(tv_json)
                uo = CSV2MD.__build_urls(tv_json.get('tv_id'), urls)
                self.db.insert(self.tv_table_name, to)
                if uo and len(uo) > 0:
                    self.db.insert_many(self.tv_urls_table_name, uo)
        except Exception as e:
            with open('error.txt', 'a', encoding='utf-8') as f:
                f.write(tv)
            logging.error(e)

    def save_init(self):
        """
        :return:
        """
        with open(self.urls_file, 'r', encoding='GB18030') as ff:
            tvs = ff.readlines()
        logging.info(f'read init tv_url data record:{len(tvs)}')
        logging.info(f'start save init {self.ft} data to mysql db')
        try:
            with ThreadPoolExecutor(max_workers=25) as e:
                e.map(self.insert_tv, tvs)
        except Exception as e:
            logging.error(e)
        logging.info(f'end save init {self.ft} data to mysql db')

    def save_timing(self):
        with open(self.urls_file, 'r', encoding='GB18030') as ff:
            tvs = ff.readlines()
        logging.info(f'read timing {self.ft} url data record:{len(tvs)}')
        logging.info(f'start save {self.ft} timing csv data to mysql db')
        try:
            if tvs and len(tvs) > 0:
                for tv in tvs:
                    tv = dict(json.loads(tv))
                    tv_name = tv.get('tv_name')
                    if tv_name:
                        m_tv = self.db.find_one(self.tv_table_name, f" tv_name=%s ", tv_name)
                        if m_tv:
                            # 已存在
                            tv_id = m_tv.get('tv_id')
                            self.db.update_tv(self.tv_table_name, f" update_time=%s ", tv.get('update_time'), tv_id)
                        else:
                            # 不存在
                            tv_id = tv.get('tv_id')
                            self.db.insert(self.tv_table_name, CSV2MD.__build_tv(tv))
                        self.db.delete(self.tv_urls_table_name, tv_id)
                        urls = list(tv.get('urls'))
                        urls = [u for u in urls if u != ' ' and u != '\t']
                        u_list = []
                        for u in urls:
                            u_list.append({'id': str(uuid.uuid4()), 'tv_id': tv_id, 'tv_url': str(u).replace(' ', '')})
                        self.db.insert_many(self.tv_urls_table_name, u_list)
        except Exception as e:
            logging.error(e)
        logging.info(f'end save timing {self.ft} data to mysql db')


