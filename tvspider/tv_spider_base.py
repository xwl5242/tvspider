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

    web_root = config.TV_SOURCE_URL
    WEB_INDEX_URL_LIST = []
    WEB_INDEX_URL_TIME_MAP = {}

    @staticmethod
    def __tv_field(field):
        """
        :return:
        """
        return str(field[0]).strip() if field and len(field) > 0 else '无'

    @staticmethod
    def __deal_detail(detail):
        """
        :param detail:
        :return:
        """
        try:
            do = {}
            details = detail.split('@')
            tv_intro = details[-1]
            t_detail = '@'.join(details[:-1]) + '@'
            tv_detail_list = [('影片名称：', 'tv_name'), ('影片演员：', 'tv_actors'), ('影片导演：', 'tv_director'),
                              ('影片类型：', 'tv_type'), ('影片地区：', 'tv_area'), ('影片语言：', 'tv_lang'),
                              ('上映日期：', 'tv_year'), ('影片备注：', 'tv_remark')]
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
            do['tv_intro'] = tv_intro
            return do
        except Exception as e:
            logging.error(e)

    async def fetch_html(self, url):
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
        :param resp:
        :return:
        """
        if resp and resp.result() and len(resp.result()) > 0:
            html = resp.result()[0]
            if html and isinstance(html, str):
                root = etree.HTML(html)
                url = root.xpath("//tr[@class='row']/td[position()=1]/a/@href")
                fetch_date = root.xpath("//tr[@class='row']/td[position()=4]//font//text()")
                for i, u in enumerate(url):
                    if u not in self.WEB_INDEX_URL_LIST:
                        self.WEB_INDEX_URL_LIST.append(u)
                        self.WEB_INDEX_URL_TIME_MAP[f'{u[1:]}'] = fetch_date[i]

    def parse_detail_html(self, resp):
        """
        :param resp:
        :return:
        """
        if resp and resp.result() and len(resp.result()) > 0:
            html = resp.result()[0]
            refer = resp.result()[1]
            refer = str(refer).replace(self.web_root, '')
            if html and isinstance(html, str):
                root = etree.HTML(html)
                tv_id = str(uuid.uuid4())
                tv_img = TVSpiderBase.__tv_field(root.xpath("//div[@class='img']/img/@src"))
                detail_xpath_str = "//table[@style='text-align:left']/tr[1]/td[2]/table//tr//td//text()"
                urls_xpath_str_1 = "//table[@style='text-align:left']/tr[2]/td/table//tr[position()<(last())]//text()"
                urls_xpath_str_2 = "//table[@style='text-align:left']/tr[3]/td/table//tr[position()<(last())]//text()"
                detail = "@".join(root.xpath(detail_xpath_str)).strip()
                tv_vo = TVSpiderBase.__deal_detail(detail)
                update_time = self.WEB_INDEX_URL_TIME_MAP.get(refer, '')
                tv_vo['tv_id'] = tv_id
                tv_vo['tv_img'] = tv_img
                tv_vo['update_time'] = update_time
                urls1 = root.xpath(urls_xpath_str_1)
                urls1 = [u for u in urls1 if u]
                urls2 = root.xpath(urls_xpath_str_2)
                urls2 = [u for u in urls2 if u]
                tv_vo['urls1'] = urls1
                tv_vo['urls2'] = urls2
                with open('urls.txt', 'a', encoding='gb18030') as f:
                    f.write(json.dumps(tv_vo, ensure_ascii=False)+'\n')

    def to_cvs(self, urls, fetch_func, parse_func):
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

    def batch_(self, urls, fetch_func, parse_func):
        """
        :return:
        """
        batch = int(len(urls) / 50) + 1
        for i in range(batch):
            end = len(urls) if i == (batch - 1) else (i + 1) * 50
            self.to_cvs(urls[i * 50:end], fetch_func, parse_func)
