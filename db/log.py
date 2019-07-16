# -*- coding:utf-8 -*-
import logging

__all__ = ['logging']

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
                    datefmt='%a, %d %b %Y %H:%M:%S', filename="spider.log", filemode='a')

