# 数据库连接模块

import mysql.connector
from mysql.connector import Error
from server.config import config

class Database:
    def __init__(self, config_name='default'):
        self.config = config[config_name]
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """连接到数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                database=self.config.DB_NAME
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return True
        except Error as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """执行查询语句"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            return result
        except Error as e:
            print(f"查询执行错误: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """执行更新语句（INSERT, UPDATE, DELETE）"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"更新执行错误: {e}")
            self.connection.rollback()
            return 0
    
    def execute_many(self, query, params_list):
        """批量执行更新语句"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.executemany(query, params_list)
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            print(f"批量执行错误: {e}")
            self.connection.rollback()
            return 0

# 创建数据库实例
db = Database()
