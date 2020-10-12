# -*- coding: utf-8 -*-

import pymysql
from DBUtils.PooledDB import PooledDB
import redis
from pymongo import MongoClient


class connMysql(object):
    def __init__(self, db=None, config=None):
        self.conn = pymysql.connect(db=db, **config, charset='utf8')
        self.cursor = self.conn.cursor()

    def query_one(self, sql):  # 返回一个元组(),如:(1,)
        try:
            con = self.conn
            curs = con.cursor()
            curs.execute(sql)
            rs = curs.fetchone()
            return rs
        except pymysql.Error as e:
            raise e

    def query_all(self, sql):  # 返回一个嵌套的元组(()),如:((1,),)
        try:
            con = self.conn
            curs = con.cursor()
            curs.execute(sql)
            rs = curs.fetchall()
            return rs
        except pymysql.Error as e:
            raise e

    def query_to_list(self, sql):  # 元组结果转换成list
        res = self.query_all(sql)
        resList = []
        for rs in res:
            tmp = rs[0]
            resList.append(tmp)
        return resList

    def change_data(self, sql):  # 插入更新删除数据(inster/update/delete)
        try:
            con = self.conn
            curs = con.cursor()
            change_lines = curs.execute(sql)  # 受影响行数
            self.conn.commit()
            print('受影响的行数: %s' % change_lines)
        except pymysql.Error as e:
            raise e

    def colseDB(self):
        self.cursor.close()
        self.conn.close()


class connMysqlPool(object):
    def __init__(self, db=None, config=None):
        self.__pool = PooledDB(
            pymysql,
            db=db,
            mincached=1,
            maxcached=10,
            cursorclass=pymysql.cursors.DictCursor,
            **config)
        self.conn = self.__pool.connection()
        self.cursor = self.conn.cursor()

    def newCursor(self):
        conn = self.conn
        return conn.cursor()

    def execute_sql(self, sql):  # 返回值为受影响的行数
        self.cursor.execute(sql)

    def query_one(self, sql):  # 返回一个带title的字典,如:{'currency_id': 1}
        try:
            con = self.conn
            curs = con.cursor()
            curs.execute(sql)
            rs = curs.fetchone()
            return rs
        except pymysql.Error as e:
            raise e

    def query_all(self, sql):  ##返回一个带title的字典列表,如:[{'currency_id': 1}]
        try:
            con = self.conn
            curs = con.cursor()
            curs.execute(sql)
            rs = curs.fetchall()
            return rs
        except pymysql.Error as e:
            raise e

    def delete_data(self, sql):
        try:
            con = self.conn
            curs = con.cursor()
            change_lines = curs.execute(sql)
            self.conn.commit()
            print('受影响的行数: %s' % change_lines)
        except pymysql.Error as e:
            raise e

    def update_data(self, sql):
        try:
            con = self.conn
            curs = con.cursor()
            change_lines = curs.execute(sql)
            self.conn.commit()
            print('受影响的行数: %s' % change_lines)
        except pymysql.Error as e:
            raise e

    def insert_data(self, sql):
        try:
            con = self.conn
            curs = con.cursor()
            change_lines = curs.execute(sql)
            self.conn.commit()
            print('受影响的行数: %s' % change_lines)
        except pymysql.Error as e:
            raise e

    def closeDBPool(self):
        self.cursor.close()
        self.conn.close()


class connRedis(object):
    def __init__(self, db=None, config=None):
        self.redisDB = db
        self.redisConfig = config
        self.__redis = redis.StrictRedis(db=db, **config)

    def get(self, key):
        if self.__redis.exists(key):
            return self.__redis.get(key)
        else:
            return ""

    def set(self, key, value):
        self.__redis.set(key, value)

    # 连接池方式及pipe
    def redisPool(self):
        pool = redis.ConnectionPool(db=self.redisDB, **self.redisConfig)
        r = redis.StrictRedis(connection_pool=pool)
        return r

    # 缓冲多条命令，然后一次性执行，减少服务器-客户端之间TCP数据库包，从而提高效率
    def pipline(self):
        return self.redisPool().pipeline(transaction=True)  # True为打开同时请求多个指令的功能

    def pipeGet(self, key):
        return self.pipline().get(key)

    def pipeSet(self, key, value):
        self.pipline().set(key, value)


class connMongoDB(object):
    def get_db(self):
        # 建立连接
        client = MongoClient(host="192.168.1.2", port=3306)
        db = client['example']
        # 或者 db = client.example
        return db

    def get_collection(self, db):
        # 选择集合（mongo中collection和database都是延时创建的）
        coll = db['informations']
        print(db.collection_names())
        return coll

    def insert_one_doc(self, db):
        # 插入一个document
        coll = db['informations']
        information = {"name": "ggg", "age": "25"}
        information_id = coll.insert(information)
        print(information_id)

    def insert_multi_docs(self, db):
        # 批量插入documents,插入一个数组
        coll = db['informations']
        information = [{"name": "xiaoming", "age": "25"}, {"name": "xiaoqiang", "age": "24"}]
        information_id = coll.insert(information)
        print(information_id)

    def get_one_doc(self, db):
        # 有就返回一个，没有就返回None
        coll = db['informations']
        print(coll.find_one())  # 返回第一条记录
        print(coll.find_one({"name": "ggg"}))
        print(coll.find_one({"name": "none"}))

    def get_one_by_id(self, db):
        # 通过objectid来查找一个doc
        coll = db['informations']
        obj = coll.find_one()
        obj_id = obj["_id"]
        print("_id 为ObjectId类型，obj_id:" + str(obj_id))

        print(coll.find_one({"_id": obj_id}))
        # 需要注意这里的obj_id是一个对象，不是一个str，使用str类型作为_id的值无法找到记录
        print("_id 为str类型 ")
        print(coll.find_one({"_id": str(obj_id)}))
        # 可以通过ObjectId方法把str转成ObjectId类型
        from bson.objectid import ObjectId

        print("_id 转换成ObjectId类型")
        print(coll.find_one({"_id": ObjectId(str(obj_id))}))

    def get_many_docs(self, db):
        # mongo中提供了过滤查找的方法，可以通过各种条件筛选来获取数据集，还可以对数据进行计数，排序等处理
        coll = db['informations']
        # ASCENDING = 1 升序;DESCENDING = -1降序;default is ASCENDING
        for item in coll.find().sort("age", pymongo.DESCENDING):
            print(item)

        count = coll.count()
        print("集合中所有数据 %s个" % int(count))

        # 条件查询
        count = coll.find({"name": "quyang"}).count()
        print("quyang: %s" % count)

    def clear_all_datas(self, db):
        # 清空一个集合中的所有数据
        db["informations"].remove()
