#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import json
import uuid
from config import config
import random
import asyncio
import aiohttp
from lxml import etree
from db.log import logging


class TVSpiderBase:

    def __init__(self, ft):
        self.ft = ft
        self.web_root = config.TV_FS_URL_MAP.get(ft)
        self.urls_file = config.TV_FS_FILE_MAP.get(ft)
        self.xpaths = config.TV_FS_XPATH_MAP.get(ft)
        self.WEB_INDEX_URL_LIST = []
        self.WEB_INDEX_URL_TIME_MAP = {}

    @staticmethod
    def __tv_field(field):
        """
        :return:
        """
        return str(field[0]).strip() if field and len(field) > 0 else '无'

    @staticmethod
    def __deal_main_detail(ft, detail):
        """
        :param detail:
        :return:
        """
        try:
            do = {}
            if ft == config.TV_TYPE_MAIN:
                details = detail.split('@')
                tv_intro = details[-1]
                do['tv_intro'] = tv_intro
                t_detail = '@'.join(details[:-1]) + '@'
                tv_detail_list = [('影片名称：', 'tv_name'), ('影片演员：', 'tv_actors'), ('影片导演：', 'tv_director'),
                                  ('影片类型：', 'tv_type'), ('影片地区：', 'tv_area'), ('影片语言：', 'tv_lang'),
                                  ('上映日期：', 'tv_year'), ('影片备注：', 'tv_remark')]
            else:
                t_detail = detail
                tv_detail_list = [('影片名称: ', 'tv_name'), ('影片主演: ', 'tv_actors'), ('影片导演: ', 'tv_director'),
                                  ('栏目分类: ', 'tv_type'), ('影片地区: ', 'tv_area'), ('语言分类:', 'tv_lang'),
                                  ('上映年份: ', 'tv_year'), ('影片备注: ', 'tv_remark')]
            t_d_t = [x[0] for x in tv_detail_list]
            for td in tv_detail_list:
                do[td[1]] = ''
                if td[0] in t_detail:
                    try:
                        d_i = t_detail.index(td[0])
                        if d_i >= 0:
                            f_h_i_1 = t_detail.index('@', d_i)
                            if f_h_i_1 >= 0:
                                f_h_i_2 = t_detail.index('@', f_h_i_1 + 1)
                                tt_d = t_detail[f_h_i_1 + 1:f_h_i_2]
                                if len([y for y in t_d_t if y not in tt_d]) == 8:
                                    do[td[1]] = tt_d
                                else:
                                    do[td[1]] = ''
                    except ValueError as e:
                        do[td[1]] = ''
                        continue
            return do
        except Exception as e:
            logging.error(e)

    @staticmethod
    async def fetch_html(url):
        """
        :return:
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': random.choice(config.UAS)}
                async with session.get(url, headers=headers, verify_ssl=False) as response:
                    return await response.text(errors='ignore'), response.url
        except Exception as e:
            logging.error(repr(e))

    def parse_index_html(self, resp):
        """
        解析主链接
        :param resp:
        :return:
        """
        if resp and resp.result() and len(resp.result()) > 0:
            html = resp.result()[0]
            ft = config.TV_FS_URL_MAP_RE.get(self.web_root)
            if html and isinstance(html, str):
                root = etree.HTML(html)
                tv_type = root.xpath(config.TV_FS_XPATH_MAP.get(ft).get('tv_index_type_xpath'))
                url = root.xpath(config.TV_FS_XPATH_MAP.get(ft).get('tv_index_url_xpath'))
                fetch_date = root.xpath(config.TV_FS_XPATH_MAP.get(ft).get('tv_index_fetch_date_xpath'))
                for i, u in enumerate(url):
                    if tv_type[i] not in config.TV_EXCLUDE_TYPE:
                        if u not in self.WEB_INDEX_URL_LIST:
                            self.WEB_INDEX_URL_LIST.append(u)
                            self.WEB_INDEX_URL_TIME_MAP[f'{u[1:]}'] = fetch_date[i]
                            # with open(config.TV_FS_INDEX_URL_FILE_MAP.get(ft), 'a', encoding='gb18030') as f:
                            #     f.write(json.dumps({'iu': u[1:], 'fd': fetch_date[i]}, ensure_ascii=False) + '\n')

    def parse_detail_html(self, resp):
        """
        解析主链接中的视频的详情，地址
        :param resp:
        :return:
        """
        if resp and resp.result() and len(resp.result()) > 0:
            html = resp.result()[0]
            refer = resp.result()[1]
            refer = str(refer).replace(self.web_root, '')
            ft = config.TV_FS_URL_MAP_RE.get(self.web_root)
            if html and isinstance(html, str):
                root = etree.HTML(html)
                tv_id = str(uuid.uuid4())
                detail_xpath_str = config.TV_FS_XPATH_MAP.get(ft).get('tv_detail_intro_xpath')
                detail = "@".join(root.xpath(detail_xpath_str)).strip()
                tv_vo = TVSpiderBase.__deal_main_detail(self.ft, detail)
                if ft == config.TV_TYPE_3PART:
                    intro_xpath_str = config.TV_FS_XPATH_MAP.get(ft).get('tv_intro_xpath')
                    intro = ''.join(root.xpath(intro_xpath_str)).replace(' ', '')
                    tv_vo['tv_intro'] = intro
                img_xpath_str = config.TV_FS_XPATH_MAP.get(ft).get('tv_detail_img_xpath')
                tv_img = TVSpiderBase.__tv_field(root.xpath(img_xpath_str))
                urls_xpath_str = config.TV_FS_XPATH_MAP.get(ft).get('tv_detail_urls_xpath')
                update_time = self.WEB_INDEX_URL_TIME_MAP.get(refer, '')
                urls = root.xpath(urls_xpath_str)
                urls = [u for u in urls if u]
                tv_vo['tv_id'] = tv_id
                tv_vo['tv_img'] = tv_img
                tv_vo['update_time'] = update_time
                tv_vo['urls'] = urls
                with open(config.TV_FS_FILE_MAP.get(ft), 'a', encoding='gb18030') as f:
                    f.write(json.dumps(tv_vo, ensure_ascii=False)+'\n')

    @staticmethod
    def save_(urls, fetch_func, parse_func):
        """
        :return:
        """
        if urls and len(urls) > 0:
            loop = asyncio.get_event_loop()
            tasks = []
            for url in urls:
                if url and url != '无':
                    task = asyncio.ensure_future(fetch_func(url))
                    task.add_done_callback(parse_func)
                    tasks.append(task)
            tasks = asyncio.gather(*tasks)
            loop.run_until_complete(tasks)

    @staticmethod
    def batch_(urls, fetch_func, parse_func):
        """
        :return:
        """
        batch = int(len(urls) / 100) + 1
        for i in range(batch):
            end = len(urls) if i == (batch - 1) else (i + 1) * 100
            TVSpiderBase.save_(urls[i * 100:end], fetch_func, parse_func)


