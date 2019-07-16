# -*- coding:utf-8 -*-
import os
import configparser

cp = configparser.ConfigParser()
cpath = os.path.dirname(os.path.abspath(__file__))+r'/config.ini'
cp.read(cpath, encoding='gb18030')
# user_agents
UAS = [
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)"
        ]

# 运行环境
__RUN = str(cp.get('RUN', 'run_platform'))

# mongodb配置相关
MD_HOST = str(cp.get('MONGODB', 'host'))
MD_PORT = int(cp.get('MONGODB', 'port'))
MD_DATABASE = str(cp.get('MONGODB', 'database'))
MD_USER = str(cp.get('MONGODB', 'user'))
MD_PWD = str(cp.get('MONGODB', 'pwd'))

# tv_spider相关
TV_SOURCE_URL = str(cp.get('TV_SPIDER', 'tv_source_url'))

if __name__ == '__main__':
    print(MD_DATABASE)

