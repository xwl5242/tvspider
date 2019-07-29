#!/usr/local/python3/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from db.mysqldb import DB


class FetchTVAll:

    def __init__(self):
        self.db = DB()

    def update(self):
        sql = f"insert into t_tv_all(tv_id,tv_ids,tv_name,tv_actors,tv_director,tv_type,tv_area," \
              f"tv_lang,tv_year,tv_img,tv_intro,update_time,img_save) select B.tv_id,B.tv_ids,B.tv_name," \
              f"B.tv_actors,B.tv_director,B.tv_type,B.tv_area,B.tv_lang,B.tv_year,B.tv_img,B.tv_intro,B.update_time," \
              f"'0' as img_save from(select A.tv_id,group_concat(A.tv_id) tv_ids,A.tv_name,A.tv_img,A.tv_actors," \
              f"A.tv_director,A.tv_type,A.tv_area,A.tv_lang,A.tv_year,A.tv_intro,A.update_time from " \
              f"(select * from t_tv union select * from t_tv_3part) A group by A.tv_name) B on duplicate " \
              f"key update update_time=B.update_time"

        self.db.execute(sql)


if __name__ == '__main__':
    fta = FetchTVAll()
    fta.update()

