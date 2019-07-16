# -*- coding:utf-8 -*-
import config
from pymongo import MongoClient, ASCENDING, DESCENDING


class DB:

    def __init__(self):
        """
        MongoDB初始化
        """
        self.conn = MongoClient(host=config.MD_HOST, port=config.MD_PORT)
        self.db = self.conn[config.MD_DATABASE]
        self.db.authenticate(config.MD_USER, config.MD_PWD)

    @classmethod
    def __get_sort(cls, s):
        if s == 'asc':
            # 升序
            return ASCENDING
        elif s == 'desc':
            # 降序
            return DESCENDING

    def get_state(self):
        """
        MongoDB的状态
        :return:
        """
        return self.conn is not None and self.db is not None

    def insert_one(self, col, data):
        """
        新增一条记录
        :param col: 集合
        :param data: 数据
        :return:
        """
        assert data, 'data not is null'
        assert isinstance(data, dict), 'data应为dict格式，如：{"id":111, "name":"zhangsan"}'
        if self.get_state():
            ret = self.db[col].insert_one(data)
            return ret.inserted_id
        else:
            return ''

    def insert_many(self, col, data):
        """
        新增多条记录
        :param col: 集合
        :param data: 数据
        :return:
        """
        assert data, 'data不为null'
        assert isinstance(data, (list, dict)), 'data应为list或dict格式，如：[{},{},{}...]'
        if self.get_state():
            ret = self.db[col].insert_many(data)
            return ret.inserted_ids
        else:
            return ''

    def update(self, col, data):
        """
        更新数据
        :param col: 集合
        :param data:
        :return:
        """
        assert data, 'data不为null'
        assert isinstance(data, dict), 'data应为dict格式，如：{"id":111}'
        if self.get_state():
            # data_filter: 过滤条件；data_revised: set设置
            data_filter, data_revised = {}, {}
            for key in data.keys():
                data_filter[key] = data[key][0]
                data_revised[key] = data[key][1]
            if self.get_state():
                return self.db[col].update_many(data_filter, {"$set": data_revised}).modified_count
            return 0

    def find_one(self, col, condition):
        """
        查询一个
        :param col: 集合
        :param condition: 查询条件
        :return:
        """
        condition = condition if condition else {}
        assert isinstance(condition, dict), 'condition应为dict格式，如：{"id":111}'
        if self.get_state():
            return self.db[col].find_one(condition)
        else:
            return None

    def find(self, col, condition, sort_fields, skip=None, limit=None):
        """
        查询多个
        :param col: 集合
        :param condition: 查询条件
        :param sort_fields: 排序和索引
        :param skip: 偏移
        :param limit: limit
        :return:
        """
        condition = condition if condition else {}
        sort_fields = sort_fields if sort_fields else ()
        assert isinstance(condition, dict), 'condition应为dict格式，如:{"id":1}'
        assert isinstance(sort_fields, list), 'sort_feilds应为tuple格式，如：[(id,asc/desc),(name,asc/desc)]'
        if self.get_state():
            sort_list = []
            # 排序处理，将asc替换为mongo里的1，desc --> -1
            if sort_fields and len(sort_fields) > 0:
                for s in sort_fields:
                    sort_list.append((s[0], DB.__get_sort(s[1])))
            # 如果有排序存在设置索引
            if sort_list and len(sort_list) > 0:
                self.db[col].create_index(sort_list)
            # 查询
            cursor = self.db[col].find(condition)
            # 设置排序
            if sort_list and len(sort_list) > 0:
                cursor.sort(sort_list)
            # 设置偏移
            if skip and skip != 0:
                cursor.skip(skip)
            # 设置limit
            if limit and limit != 0:
                cursor.limit(limit)
            return cursor
        else:
            return None

    def delete(self, col, condition):
        """
        删除数据
        :param col: 集合
        :param condition: 删除条件
        :return:
        """
        assert isinstance(condition, dict), 'condition应为dict格式，如：{"id":1}'
        if self.get_state():
            return self.db[col].delete_many(filter=condition).deleted_count
        return 0

    def count(self, col, condition):
        """
        统计个数
        :param col: 集合
        :param condition: 查询条件
        :return:
        """
        condition = condition if condition else {}
        if self.get_state():
            return self.db[col].count_documents(condition)


if __name__ == '__main__':
    db = DB()
    # db.delete('t_tv', {})
    # db.delete('t_tv_urls', {})
    # print(db.count('t_tv', {}))
    # print(db.count('t_tv_urls', {}))
    # db.insert_one('t_f_u', {'id': '1', 'f_title': '优视频', 'f_url': 'http://www.yoviptv.com', 'del_flag': '0'})
    print(db.count('t_tv_banner_top', {}))

