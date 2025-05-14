import logging
from typing import Union

from tinydb import Query, TinyDB

# 数据库连接
log = logging.getLogger(__name__)


class JsonCache:
    """json 数据库
    使用 json 文件存储，方便直接修改
    """

    def __init__(self, cache_url: str):
        log.info(f"连接数据库: {cache_url}")
        self.cache = TinyDB(cache_url)
        self.query = Query()

    def set(self, key: str, value: Union[str, dict], tbl: str = None):
        table = self.cache.table(tbl) if tbl else self.cache
        res = table.search(self.query.key == key)
        if res:
            # log.debug("数据已存在，更新键")
            table.update({"val": value}, self.query.key == key)
        else:
            # log.debug("数据不存在，插入键")
            table.insert({"key": key, "val": value})

    def get(self, key: str, tbl: str = None, default: Union[str, dict, list] = None):
        table = self.cache.table(tbl) if tbl else self.cache
        res = table.search(self.query.key == key)
        if res:
            # log.debug("数据存在，直接返回")
            return res[0]["val"]
        # log.warning("数据不存在，返回默认值")
        return default

    def get_all(self, tbl: str = None):
        table = self.cache.table(tbl) if tbl else self.cache
        return table.all()

    def close(self):
        log.info("关闭数据库")
        self.cache.close()
