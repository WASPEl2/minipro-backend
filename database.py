import pymysql


class MysqlConnection(object):
    def __init__(self):
        self.host = "mysql-154265-0.cloudclusters.net"
        self.port = "18708"
        self.user = "admin"
        self.passwd = "WoPhVOl1"
        self.db = "SmartCanteen"

    def connect_mysql(self):
        return pymysql.connect(
            host=self.host,
            port=int(self.port),
            user=self.user,
            password=self.passwd,
            db=self.db,
        )
