from pprint import pprint

import pytest
import tomllib
from openpyxl import load_workbook

from mulaco.base import AppBase
from mulaco.db.service import DbService
from mulaco.excel.loader import ExcelLoader
from mulaco.excel.model import BatchExcel, SheetDTO


@pytest.fixture(scope="module")
def handler():

    app_base = AppBase()
    app_base.setup()
    cache = app_base.cache

    db = DbService("sqlite:///db/test.db")

    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))
    eb = BatchExcel.from_dict(d)
    excel = eb.excels[0]

    yield ExcelLoader(excel, db, cache)


# @pytest.mark.skip()
def test_handler_loader(handler: ExcelLoader):
    """手动构造并生成数据"""
    sheet_dto = handler.excel.sheets[0]
    assert isinstance(sheet_dto, SheetDTO)
    db = handler.db
    pprint(db.get_all_exsh())
    handler.set_db_exsh_meta(sheet_dto)
    res = db.get_all_exsh()
    assert len(res) > 0

    handler.set_cache_exsh_meta_data(89, 100, sheet_dto)

    # 持久化数据
    wb = load_workbook(handler.excel.src_path)
    sheet = wb[sheet_dto.sheet_name]
    handler.set_db_sheet_raw_data(sheet, sheet_dto)

    cells = db.get_all_cell_info()
    pprint(cells)
    pprint(len(cells))


def test_handler_loader_2(handler: ExcelLoader):
    """测试构造并生成数据"""
    handler.loader()
