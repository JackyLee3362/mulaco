import logging

from tinydb import Query, TinyDB

# 数据库连接
log = logging.getLogger(__name__)


class KVDB:
    """KV 数据库
    使用 json 文件存储，方便直接修改
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        log.debug("连接数据库")
        self.db = TinyDB(db_url)
        self.query = Query()

    def set(self, key: str, value: str | dict, tbl_name: str = None):
        table = self.db.table(tbl_name) if tbl_name else self.db
        res = table.search(self.query.key == key)
        if res:
            log.debug("数据已存在，更新键")
            table.update({"value": value}, self.query.key == key)
        else:
            log.debug("数据不存在，插入键")
            table.insert({"key": key, "value": value})

    def get(self, key: str, tbl_name: str = None, default: str | dict = None):
        table = self.db.table(tbl_name) if tbl_name else self.db
        res = table.search(self.query.key == key)
        if res:
            log.debug("数据存在，直接返回")
            return res[0]["value"]
        log.warning("数据不存在，返回默认值")
        return default

    def close(self):
        log.debug("关闭数据库")
        self.db.close()
