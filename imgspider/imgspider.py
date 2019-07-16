#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import config
import random
import aiohttp
import asyncio
from db.db import DB
from db.log import logging


class ImgSpider:

    def __init__(self):
        self.db = DB()

    async def fetch_html(self, url, tv_id):
        """
        :return:
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': random.choice(config.UAS)}
                async with session.get(url, headers=headers, verify_ssl=False) as response:
                    return await response.read(), tv_id
        except Exception as e:
            logging.error(repr(e))

    def parse_content(self, resp):
        if resp and resp.result() and len(resp.result()) == 2:
            resp = resp.result()
            with open(f'/home/img/{resp[1]}.jpg', 'wb') as f:
                f.write(resp[0])
            self.db.update('t_tv', {"tv_id": [resp[1], resp[1]], "img_save": ['0', '1']})

    def batch_(self):
        """
        :return:
        """
        tvs = self.db.find('t_tv', {"img_save": '0'}, [('update_time', 'desc')])
        tvs = [(tv['tv_id'], tv['tv_img']) for tv in tvs]
        batch = int(len(tvs) / 50) + 1
        for i in range(batch):
            end = len(tvs) if i == (batch - 1) else (i + 1) * 50
            self.download(tvs[i * 50:end])

    def download(self, tvs):
        loop = asyncio.get_event_loop()
        tasks = []
        for tv in tvs:
            tid, url = tv[0], tv[1]
            if url:
                task = asyncio.ensure_future(self.fetch_html(url, tid))
                task.add_done_callback(self.parse_content)
                tasks.append(task)
        tasks = asyncio.gather(*tasks)
        loop.run_until_complete(tasks)


if __name__ == '__main__':
    import time
    s = time.time()
    imgs = ImgSpider()
    imgs.batch_()
    print(int(time.time()-s))

