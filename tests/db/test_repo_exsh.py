import sqlite3
from pprint import pprint

import pytest

from mulaco.db.repo import ExcelSheetRepo
from mulaco.db.db import DbService
from mulaco.models.po_model import ExcelSheetPO


@pytest.fixture(scope="module")
def repo(mem: DbService):
    repo = ExcelSheetRepo(session=mem.session)
    e1s1 = ExcelSheetPO(excel="ex1", sheet="sh1", header=1)
    e1s2 = ExcelSheetPO(excel="ex1", sheet="sh2", header=2)
    e2s1 = ExcelSheetPO(excel="ex2", sheet="sh1", header=3)
    e3s1 = ExcelSheetPO(excel="ex3", sheet="sh1", header=4)
    repo.insert_all([e1s1, e1s2, e2s1, e3s1])
    repo.session.commit()
    yield repo


# FIX
@pytest.mark.skip("测试失败，会发生错误，但是捕获不到")
def test_测试_exsh_插入失败(repo: ExcelSheetRepo):
    e1s1 = ExcelSheetPO(excel="ex1", sheet="sh1", header=1)
    with pytest.raises(Exception) as e:
        repo.insert_one(e1s1)
        # 1 / 0
    print(repo.list_all())


@pytest.mark.skip()
def test_测试批量_exsh_插入失败(repo: ExcelSheetRepo):
    ex1sh1 = ExcelSheetPO(excel="ex1", sheet="sh1", header=1)
    ex1sh2 = ExcelSheetPO(excel="ex1", sheet="sh2", header=2)
    ex2sh1 = ExcelSheetPO(excel="ex2", sheet="sh1", header=3)
    ex3sh1 = ExcelSheetPO(excel="ex3", sheet="sh1", header=3)
    repo.insert_all([ex1sh1, ex1sh2, ex2sh1, ex3sh1])
    pprint(repo.list_all())


def test_测试_exsh_更新成功(repo: ExcelSheetRepo):
    pprint(repo.list_all())
    e1s1 = ExcelSheetPO(id=1, excel="ex1", sheet="sh1", header=10)
    repo.update_by_id(e1s1)
    repo.session.commit()
    pprint(repo.list_all())


def test_选择通过条件获得_exsh(repo: ExcelSheetRepo):
    pprint(repo.list_all())
    res = repo.get_list_by_cond((ExcelSheetPO.header >= 2, ExcelSheetPO.header <= 3))
    pprint(res)
