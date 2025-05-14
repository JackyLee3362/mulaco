from pprint import pprint

import pytest

from mulaco.core.app import App
from mulaco.db.db import DbService
from mulaco.db.sql import (
    build_sql_get_all_not_proc_trans,
    build_sql_get_all_not_translated_cells,
    build_sql_get_all_write_trans,
    build_sql_get_not_proc_cells,
)
from mulaco.models.bo_model import ExcelSheetBO


@pytest.fixture(scope="module")
def excel(app: App) -> ExcelSheetBO:

    excel = app.batch_excels.excels[0]
    sheet = excel.sheets[0]
    exsh = ExcelSheetBO(excel.excel_name, sheet.sheet_name, sheet.header_row)

    return exsh


def test_1(db: DbService, excel: ExcelSheetBO):
    stmt = build_sql_get_all_not_translated_cells(excel, "en", "de", 3)
    res = db.session.execute(stmt).all()
    print("未翻译的数量为", len(res))
    pprint(res)


def test_2(db: DbService, excel: ExcelSheetBO):
    stmt = build_sql_get_not_proc_cells(excel, "en", 3)
    res = db.session.execute(stmt).all()
    print("未处理的数量为", len(res))
    pprint(res)


def test_3(db: DbService, excel: ExcelSheetBO):
    stmt = build_sql_get_all_not_proc_trans(excel, "en", "de", 3)
    res = db.session.execute(stmt).all()
    print("翻译未处理的数量为", len(res))
    pprint(res)


def test_4(db: DbService, excel: ExcelSheetBO):
    stmt = build_sql_get_all_write_trans(excel, "en")
    res = db.session.execute(stmt).all()
    print("总共翻译的数量为", len(res))
    pprint(res)
