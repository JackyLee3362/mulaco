import os
from pprint import pprint

import pytest
import tomllib

from mulaco.base import AppBase
from mulaco.excel.model import BatchExcel, ExcelDTO, SheetDTO

app = AppBase()
app.setup()


def test_load_config():
    d = tomllib.load(open("config/batch1.toml", "rb"))
    pprint(d)


def test_map_dict():
    d = tomllib.load(open("config/batch1.toml", "rb"))
    BatchExcel.from_dict(d)


def test_cache_config():
    config_file = "config/batch1.toml"
    key = "excel-info"
    d = tomllib.load(open(config_file, "rb"))
    # 统计修改时间
    pprint(d)
    mtime = int(os.stat(config_file).st_mtime)
    print("修改时间", mtime)
    eb = BatchExcel.from_dict(d)
    res = app.cache.get("excel-info", config_file)
    if res is None or res["modify_time"] < mtime:
        print("需要新增")
        eb.modify_time = mtime
        d2 = eb.to_dict()
        app.cache.set(key, d2, config_file)
    res = app.cache.get_all()
    pprint(res)


def test_cache_to_model():
    CACHE_EXCEL_TBL = "excels"
    d = app.cache.get("ClothingConfig.xlsx", CACHE_EXCEL_TBL)
    res = ExcelDTO.from_dict(d)
    print(res)
