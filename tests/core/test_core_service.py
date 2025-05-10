from pprint import pprint

import pytest

from mulaco.core.db_models import CellInfo, ExcelSheet, TransInfo
from mulaco.core.service import DbService


@pytest.fixture(scope="module")
def db_service():
    return DbService("sqlite:///:memory:")


exsh = ExcelSheet(excel="ex", sheet="sh", header=1)
cell4 = CellInfo(row=4, col=2, src_lang="en")
cell5 = CellInfo(row=5, col=2, src_lang="en")
trans = TransInfo(dst_lang="zh")


def test_1_add_exsh(db_service: DbService):
    db_service.upsert_exsh(exsh)
    pprint(db_service.get_all_exsh())


def test_2_add_cell_info(db_service: DbService):
    db_service.upsert_exsh(exsh)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell4)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell5)
    pprint(db_service.get_all_exsh())
    pprint(db_service.get_all_cell_info())


def test_3_add_trans_info(db_service: DbService):
    db_service.upsert_exsh(exsh)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell4)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell5)
    db_service.add_trans_info(exsh, cell4, trans)
    pprint(db_service.get_all_exsh())
    pprint(db_service.get_all_cell_info())
    pprint(db_service.get_all_trans_info())


def test_4_get_all_trans_info(db_service: DbService):
    db_service.upsert_exsh(exsh)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell4)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell5)
    db_service.add_trans_info(exsh, cell4, trans)
    src = "en"
    dst = "zh"
    excel = "ex"
    sheet = "sh"
    col = 2
    res = db_service.get_all_translated_cell(src, dst, excel, sheet, col)
    print("已翻译的Exsh Cell Trans")
    for res_exsh, res_cell, res_trans in res:
        print(res_exsh, res_cell, res_trans)
