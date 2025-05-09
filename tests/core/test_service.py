from pprint import pprint

import pytest

from mulaco.core.db_models import CellInfo, ExcelSheet, TransInfo
from mulaco.core.service import DbService


@pytest.fixture(scope="module")
def db_service():
    return DbService("sqlite:///:memory:")


exsh = ExcelSheet(excel="ex", sheet="sh", header=1)
cell = CellInfo(row=4, col=2, src_lang="en")
trans = TransInfo(dst_lang="jp")


def test_add_exsh(db_service: DbService):
    db_service.add_exsh(exsh)
    pprint(db_service.get_all_exsh())


def test_add_cell_info(db_service: DbService):
    db_service.add_exsh(exsh)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell)
    pprint(db_service.get_all_exsh())
    pprint(db_service.get_all_cell_info())


def test_add_trans_info(db_service: DbService):
    db_service.add_exsh(exsh)
    db_service.add_cell_info(exsh.excel, exsh.sheet, cell)
    db_service.add_trans_info(exsh, cell, trans)
    pprint(db_service.get_all_exsh())
    pprint(db_service.get_all_cell_info())
    pprint(db_service.get_all_trans_info())
