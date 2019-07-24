# -*- coding:utf-8 -*-
import pymysql
from config import config
from DBUtils.PooledDB import PooledDB

# database pool
POOL = PooledDB(pymysql, 5, host=config.MS_HOST, user=config.MS_USER,
                passwd=config.MS_PWD, db=config.MS_DATABASE, port=config.MS_PORT,
                charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)


# database decorator, auto connect and auto close db, cursor
def app_db(func):
    def wrapper(*args, **kwargs):
        try:
            conn = POOL.connection()
            cursor = conn.cursor()
            return func(cursor, *args, **kwargs)
        except Exception as e:
            import traceback
            print(traceback.print_exc())
            conn.rollback()
        finally:
            conn.commit()
            cursor.close()
            conn.close()
    return wrapper


# database operator base
class DB:

    @staticmethod
    @app_db
    def insert_tv(cursor, tv):
        sql = "insert into t_tv(tv_id,tv_name,tv_img,tv_actors,tv_director,tv_type," \
              "tv_area,tv_lang,tv_year,tv_intro,tv_remark,update_time,img_save) values(" \
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (tv['tv_id'], tv['tv_name'], tv['tv_img'], tv['tv_actors'], tv['tv_director'],
                             tv['tv_type'], tv['tv_area'], tv['tv_lang'], tv['tv_year'], tv['tv_intro'],
                             tv['tv_remark'], tv['update_time'], tv['img_save'], ))

    @staticmethod
    @app_db
    def insert_urls(cursor, urls):
        for u in urls:
            sql = "insert into t_tv_urls(id,tv_id,tv_url) values (%s,%s,%s)"
            cursor.execute(sql, (u['id'], u['tv_id'], u['tv_url']))

    @staticmethod
    @app_db
    def find_tv_by_name(cursor, tv_name):
        sql = "select * from t_tv where tv_name=%s"
        cursor.execute(sql, (tv_name,))
        tv = cursor.fetchall()
        return tv[0] if tv and len(tv) > 0 else None

    @staticmethod
    @app_db
    def update_tv(cursor, tv_id, update_time):
        sql = "update t_tv set update_time=%s where tv_id=%s"
        cursor.execute(sql, (tv_id, update_time))

    @staticmethod
    @app_db
    def delete_tv_urls(cursor, tv_id):
        sql = "delete from t_tv_urls where tv_id=%s"
        cursor.execute(sql, (tv_id,))


