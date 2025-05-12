from pprint import pprint

import pytest

from mulaco.db.mapper import cell_bo_map_po, exsh_bo_map_po, trans_bo_map_po
from mulaco.db.service import DbService
from mulaco.models.business_model import CellInfoBO, ExcelSheetBO, TransInfoBO


@pytest.fixture(scope="module")
def db_service():
    return DbService("sqlite:///db/test.db")
    # return DbService("sqlite:///:memory:", True)


exsh = ExcelSheetBO(excel="ex", sheet="sh", header=1)
ex2sh = ExcelSheetBO(excel="ex2", sheet="sh", header=1)
exsh2 = ExcelSheetBO(excel="ex", sheet="sh2", header=1)
cell4 = CellInfoBO(row=4, col=2, src_lang="en")
cell5 = CellInfoBO(row=5, col=2, src_lang="en")
cell6 = CellInfoBO(row=5, col=2, src_lang="en")
trans4zh = TransInfoBO(dst_lang="zh", trans_text="你好")
trans5jp = TransInfoBO(dst_lang="jp")

cell4.exsh = exsh
cell5.exsh = exsh
cell6.exsh = ex2sh

trans4zh.cell = cell4
trans5jp.cell = cell5


def test_1_add_exsh(db_service: DbService):
    db_service.upsert_exsh(exsh_bo_map_po(exsh))
    pprint(db_service.get_all_exsh())


def test_2_add_cell_info(db_service: DbService):
    db_service.upsert_exsh(exsh_bo_map_po(exsh))
    db_service.upsert_exsh(exsh_bo_map_po(ex2sh))
    db_service.upsert_exsh(exsh_bo_map_po(exsh2))

    db_service.upsert_cell(cell_bo_map_po(cell4))
    db_service.upsert_cell(cell_bo_map_po(cell5))

    pprint(db_service.get_all_exsh())
    print("所有的 cell 数据")
    pprint(db_service.get_all_cell_info("ex2"))


def test_3_add_trans_info(db_service: DbService):
    db_service.upsert_exsh(exsh_bo_map_po(exsh))
    db_service.upsert_cell(cell_bo_map_po(cell4))
    db_service.upsert_cell(cell_bo_map_po(cell5))
    db_service.upsert_trans_info(trans_bo_map_po(trans4zh))
    pprint(db_service.get_all_exsh())
    pprint(db_service.get_all_cell_info())
    pprint(db_service.get_all_trans_info())


def test_4_get_all_trans_info(db_service: DbService):
    db_service.upsert_exsh(exsh_bo_map_po(exsh))
    db_service.upsert_exsh(exsh_bo_map_po(ex2sh))
    db_service.upsert_cell(cell_bo_map_po(cell4))
    db_service.upsert_cell(cell_bo_map_po(cell5))
    db_service.upsert_cell(cell_bo_map_po(cell6))
    db_service.upsert_trans_info(trans_bo_map_po(trans4zh))
    db_service.upsert_trans_info(trans_bo_map_po(trans5jp))
    res = db_service.get_not_translated_cells(exsh, src="en", dst="zh", col=2)
    print("未翻译的 Cell ")
    for res_cell in res:
        print(res_cell)
