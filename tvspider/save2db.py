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
        self.tv_table_name = {config.TV_TYPE_MAIN: 't_tv',
                              config.TV_TYPE_BACKUP: 't_tv_backup', config.TV_TYPE_3PART: 't_tv_3part'}.get(ft)
        self.tv_urls_table_name = {config.TV_TYPE_MAIN: 't_tv_urls',
                                   config.TV_TYPE_BACKUP: 't_tv_urls_backup', config.TV_TYPE_3PART: 't_tv_urls_3part'}.get(ft)

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

    def insert_tv_other(self, tv):
        tv_json = dict(json.loads(tv))
        tv_id = tv_json.get('id')
        tv = {'id': tv_id, 'tv_name': tv_json.get('tv_name'), 'update_time': tv_json.get('update_time')}
        self.db.insert(self.tv_table_name, tv)
        u_list = []
        for u in list(tv_json.get('urls')):
            u_list.append({'id': str(uuid.uuid4()), 'tv_id': tv_id, 'tv_url': u})
        self.db.insert_many(self.tv_urls_table_name, u_list)

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
            self.db.insert(self.tv_table_name, to)
            if uo and len(uo) > 0:
                self.db.insert_many(self.tv_urls_table_name, uo)
        except Exception as e:
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
            with ThreadPoolExecutor() as e:
                e.map(self.insert_tv if self.ft == config.TV_TYPE_MAIN else self.insert_tv_other, tvs)
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
                    m_tv = self.db.find_one(self.tv_table_name, f" tv_name=%s ", tv_name)
                    if m_tv:
                        # 已存在
                        tv_id = m_tv.get('tv_id')
                        self.db.update_tv(self.tv_table_name, f" update_time=%s ", tv.get('update_time'), tv_id)
                    else:
                        # 不存在
                        tv_id = tv.get('tv_id')
                        self.db.insert(self.tv_table_name, CSV2MD.__build_tv(tv) if self.ft == config.TV_TYPE_MAIN else tv)
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


