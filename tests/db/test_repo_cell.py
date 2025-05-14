from pprint import pprint

import pytest

from mulaco.db.repo import CellInfoRepo
from mulaco.db.db import DbService
from mulaco.models.po_model import CellInfoPO


def cell_info_factory(exsh_id, row, col, lang="en"):
    return CellInfoPO(exsh_id=exsh_id, row=row, col=col, src_lang=lang)


@pytest.fixture(scope="module")
def repo(mem: DbService):
    repo = CellInfoRepo(session=mem.session)
    c1 = CellInfoPO(exsh_id=1, row=4, col=2, src_lang="en")
    c2 = CellInfoPO(exsh_id=1, row=5, col=2, src_lang="en")
    c3 = CellInfoPO(exsh_id=2, row=4, col=2, src_lang="en")
    c4 = CellInfoPO(exsh_id=2, row=5, col=2, src_lang="en")
    repo.insert_all([c1, c2, c3, c4])
    yield repo


@pytest.mark.skip()
def test_cell_insert_one(repo: CellInfoRepo):
    c1 = CellInfoPO(exsh_id=1, row=4, col=2, src_lang="en")
    repo.insert_one(c1)
    print(repo.list_all())


@pytest.mark.skip()
def test_cell_insert_all(repo: CellInfoRepo):
    c1 = CellInfoPO(id=1, exsh_id=1, row=4, col=2, src_lang="en")
    c2 = CellInfoPO(id=2, exsh_id=1, row=5, col=2, src_lang="en")
    c3 = CellInfoPO(id=3, exsh_id=2, row=4, col=2, src_lang="en")
    c4 = CellInfoPO(id=4, exsh_id=2, row=5, col=2, src_lang="en")
    repo.insert_all([c1, c2, c3, c4])
    pprint(repo.list_all())


def test_cell_update(repo: CellInfoRepo):
    # 准备数据
    pprint(repo.list_all())
    c1 = CellInfoPO(id=1, exsh_id=1, row=4, col=2, src_lang="en", raw_text="raw-text")
    repo.update_by_id(c1)
    pprint(repo.list_all())
