import pymysql


class SqlHelper(object):
    def __init__(self, host, port, username, password, db, charset='utf8'):
        # 读取配置文件
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = db
        self.charset = charset
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(host=self.host,
                                    port=self.port,
                                    user=self.username,
                                    passwd=self.password,
                                    db=self.db,
                                    charset=self.charset)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def get_list(self, sql, args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchall()
        return result

    def get_one(self, sql, args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchone()
        return result

    def modify(self, sql, args):
        self.cursor.execute(sql, args)
        self.conn.commit()

    def multiple_modify(self, sql, args):
        self.cursor.executemany(sql, args)
        self.conn.commit()

    def create(self, sql, args):
        self.cursor.execute(sql, args)
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.cursor.close()
        self.conn.close()
