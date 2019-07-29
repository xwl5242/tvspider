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
        conn = POOL.connection()
        cursor = conn.cursor()
        try:
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
    def execute(cursor, sql):
        cursor.execute(sql)

    @staticmethod
    @app_db
    def insert(cursor, table_name, tv):
        assert isinstance(tv, dict), 'insert param need dict type'
        tv = dict(tv)
        columns = ','.join(tv.keys())
        columns_s = ''.join(['%s,' for i in tv.keys()])[:-1]
        sql = f"insert into {table_name}({columns}) values ({columns_s})"
        cursor.execute(sql, tuple([tv.get(k) for k in tv.keys()]))

    @staticmethod
    @app_db
    def insert_many(cursor, table_name, tvs):
        tv = list(tvs)[0]
        tv_list = []
        for t in tvs:
            tv_list.append(tuple([t.get(k) for k in t.keys()]))
        columns = ','.join(tv.keys())
        columns_s = ''.join(['%s,' for i in tv.keys()])[:-1]
        sql = f"insert into {table_name}({columns}) values ({columns_s})"
        cursor.executemany(sql, tv_list)

    @staticmethod
    @app_db
    def find_one(cursor, table_name, where_str, args):
        assert isinstance(where_str, str), 'where need str type'
        sql = f"select * from {table_name} where 1=1 and {where_str}"
        cursor.execute(sql, args)
        tv = cursor.fetchall()
        return tv[0] if tv and len(tv) > 0 else None

    @staticmethod
    @app_db
    def find_all(cursor, table_name, where_str, args):
        sql = f"select * from {table_name} where 1=1 and {where_str}"
        cursor.execute(sql, args)
        tvs = cursor.fetchall()
        return tvs if tvs and len(tvs) > 0 else []

    @staticmethod
    @app_db
    def update_tv(cursor, table_name, update_str, update_args, tv_id):
        sql = f"update {table_name} set {update_str} where tv_id=%s"
        cursor.execute(sql, (update_args, tv_id))

    @staticmethod
    @app_db
    def delete(cursor, table_name, tv_id):
        sql = f"delete from {table_name} where tv_id=%s"
        cursor.execute(sql, (tv_id,))

    @staticmethod
    @app_db
    def delete_by_tv_type(cursor, table_name, tv_type):
        sql = f"delete from {table_name} where tv_type=%s"
        cursor.execute(sql, (tv_type,))


