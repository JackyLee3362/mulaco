from mulaco.base.db import JsonCache
from mulaco.db.service import DbService
from mulaco.excel.model import ExcelDTO


class ExcelHandler:
    CACHE_TBL = "excels"

    def __init__(self, excel: ExcelDTO, db: DbService, cache: JsonCache):
        self.excel = excel
        self.db = db
        self.cache = cache
