# -*- coding:utf-8 -*-
import os
import configparser

cp = configparser.ConfigParser()
cp.read(os.path.dirname(os.path.abspath(__file__))+r'/config.ini', encoding='utf-8')

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

# mongodb setting
MD_HOST = str(cp.get('MONGODB', 'host'))
MD_PORT = int(cp.get('MONGODB', 'port'))
MD_DATABASE = str(cp.get('MONGODB', 'database'))
MD_USER = str(cp.get('MONGODB', 'user'))
MD_PWD = str(cp.get('MONGODB', 'pwd'))

# mysql setting
MS_HOST = str(cp.get('MYSQL', 'host'))
MS_PORT = int(cp.get('MYSQL', 'port'))
MS_DATABASE = str(cp.get('MYSQL', 'database'))
MS_USER = str(cp.get('MYSQL', 'user'))
MS_PWD = str(cp.get('MYSQL', 'pwd'))

TV_TYPE_MAIN = 'MAIN'
TV_TYPE_BACKUP = 'BACKUP'
TV_TYPE_3PART = '3PART'

# tv_spider_url相关
TV_FS_MAIN_URL = str(cp.get('TV_SPIDER_URL', 'tv_fs_main'))
TV_FS_BACKUP_URL = str(cp.get('TV_SPIDER_URL', 'tv_fs_backup'))
TV_FS_3PART_URL = str(cp.get('TV_SPIDER_URL', 'tv_fs_3part'))
TV_FS_URL_MAP = {TV_TYPE_MAIN: TV_FS_MAIN_URL, TV_TYPE_BACKUP: TV_FS_BACKUP_URL, TV_TYPE_3PART: TV_FS_3PART_URL}
TV_FS_URL_MAP_RE = {TV_FS_MAIN_URL: TV_TYPE_MAIN, TV_FS_BACKUP_URL: TV_TYPE_BACKUP, TV_FS_3PART_URL: TV_TYPE_3PART}

# tv_spider_index_url_file 相关
TV_FS_INDEX_MAIN_FILE = str(cp.get('TV_SPIDER_INDEX_FILE', 'tv_fs_main_file'))
TV_FS_INDEX_BACKUP_FILE = str(cp.get('TV_SPIDER_INDEX_FILE', 'tv_fs_backup_file'))
TV_FS_INDEX_3PART_FILE = str(cp.get('TV_SPIDER_INDEX_FILE', 'tv_fs_3part_file'))
TV_FS_INDEX_URL_FILE_MAP = {TV_TYPE_MAIN: TV_FS_INDEX_MAIN_FILE,
                            TV_TYPE_BACKUP: TV_FS_INDEX_BACKUP_FILE, TV_TYPE_3PART: TV_FS_INDEX_3PART_FILE}

# tv_spider_url_file相关
TV_FS_MAIN_FILE = str(cp.get('TV_SPIDER_URL_FILE', 'tv_fs_main_file'))
TV_FS_BACKUP_FILE = str(cp.get('TV_SPIDER_URL_FILE', 'tv_fs_backup_file'))
TV_FS_3PART_FILE = str(cp.get('TV_SPIDER_URL_FILE', 'tv_fs_3part_file'))
TV_FS_FILE_MAP = {TV_TYPE_MAIN: TV_FS_MAIN_FILE, TV_TYPE_BACKUP: TV_FS_BACKUP_FILE, TV_TYPE_3PART: TV_FS_3PART_FILE}
TV_FS_TIMIMG_FILE_MAP = {TV_TYPE_MAIN: 'timing_main.txt', TV_TYPE_BACKUP: 'timing_backup.txt', TV_TYPE_3PART: 'timing_3part.txt'}

# tv_spider_xpath相关
TV_FS_MAIN_XPATH = {}
for option in cp.options('TV_SPIDER_XPATH_MAIN'):
    TV_FS_MAIN_XPATH[option] = str(cp.get('TV_SPIDER_XPATH_MAIN', option))
TV_FS_BACKUP_XPATH = {}
for option in cp.options('TV_SPIDER_XPATH_BACKUP'):
    TV_FS_BACKUP_XPATH[option] = str(cp.get('TV_SPIDER_XPATH_BACKUP', option))
TV_FS_3PART_XPATH = {}
for option in cp.options('TV_SPIDER_XPATH_3PART'):
    TV_FS_3PART_XPATH[option] = str(cp.get('TV_SPIDER_XPATH_3PART', option))
TV_FS_XPATH_MAP = {TV_TYPE_MAIN: TV_FS_MAIN_XPATH, TV_TYPE_BACKUP: TV_FS_BACKUP_XPATH, TV_TYPE_3PART: TV_FS_3PART_XPATH}


if __name__ == '__main__':
    print(TV_FS_URL_MAP)
    print(TV_FS_XPATH_MAP)

