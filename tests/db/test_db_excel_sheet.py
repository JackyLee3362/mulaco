from pprint import pprint

import pytest

from mulaco.db.repo import ExcelSheetRepo
from mulaco.db.service import DbService
from mulaco.models.db_model import ExcelSheetPO


@pytest.fixture(scope="module")
def db():
    cli = DbService("sqlite:///:memory:")
    db = ExcelSheetRepo(session=cli.session)
    ex1sh1 = ExcelSheetPO(excel="excel-1", sheet="sheet-1", header=1)
    ex1sh2 = ExcelSheetPO(excel="excel-1", sheet="sheet-2", header=2)
    ex2sh1 = ExcelSheetPO(excel="excel-2", sheet="sheet-1", header=3)
    ex3sh1 = ExcelSheetPO(excel="excel-3", sheet="sheet-1", header=4)
    db.insert_all([ex1sh1, ex1sh2, ex2sh1, ex3sh1])
    yield db


@pytest.mark.skip()
def test_excel_insert_one(db: ExcelSheetRepo):
    ex1sh1 = ExcelSheetPO(excel="excel-1", sheet="sheet-1", header=1)
    db.insert_one(ex1sh1)
    print(db.list_all())


@pytest.mark.skip()
def test_excel_insert_all(db: ExcelSheetRepo):
    ex1sh1 = ExcelSheetPO(excel="excel-1", sheet="sheet-1", header=1)
    ex1sh2 = ExcelSheetPO(excel="excel-1", sheet="sheet-2", header=2)
    ex2sh1 = ExcelSheetPO(excel="excel-2", sheet="sheet-1", header=3)
    ex3sh1 = ExcelSheetPO(excel="excel-3", sheet="sheet-1", header=3)
    db.insert_all([ex1sh1, ex1sh2, ex2sh1, ex3sh1])
    pprint(db.list_all())


def test_excel_sheet_update(db: ExcelSheetRepo):
    pprint(db.list_all())
    _ex1sh1 = ExcelSheetPO(id=1, excel="excel-1", sheet="sheet-1", header=10)
    ex1sh1 = db.get_exsh_by_uk(_ex1sh1)
    ex1sh1.header = 100
    db.update_by_id(ex1sh1)
    db.session.commit()
    pprint(db.list_all())


def test_excel_sheet_select_by_condi(db: ExcelSheetRepo):
    pprint(db.list_all())
    res = db.get_list_by_cond((ExcelSheetPO.header >= 2, ExcelSheetPO.header <= 3))
    pprint(res)
