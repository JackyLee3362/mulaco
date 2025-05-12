from pprint import pprint

import pytest

from mulaco.db.repo import CellInfoRepo
from mulaco.db.service import DbService
from mulaco.models.db_model import CellInfoPO


def cell_info_factory(exsh_id, row, col, lang="en"):
    return CellInfoPO(
        exsh_id=exsh_id,
        row=row,
        col=col,
        src_lang=lang,
    )


@pytest.fixture(scope="module")
def db():
    cli = DbService("sqlite:///:memory:")
    db = CellInfoRepo(session=cli.session)
    c1 = cell_info_factory(1, 4, 2)
    c2 = cell_info_factory(1, 5, 2)
    c3 = cell_info_factory(2, 4, 2)
    c4 = cell_info_factory(2, 5, 2)
    db.insert_all([c1, c2, c3, c4])
    yield db


@pytest.mark.skip()
def test_cell_insert_one(db: CellInfoRepo):
    c1 = cell_info_factory(1, 4, 2)
    db.insert_one(c1)
    print(db.list_all())


@pytest.mark.skip()
def test_cell_insert_all(db: CellInfoRepo):
    c1 = cell_info_factory(1, 4, 2)
    c2 = cell_info_factory(1, 5, 2)
    c3 = cell_info_factory(2, 4, 2)
    c4 = cell_info_factory(2, 5, 2)
    db.insert_all([c1, c2, c3, c4])
    pprint(db.list_all())


def test_cell_update(db: CellInfoRepo):
    # 准备数据
    pprint(db.list_all())
    c1 = cell_info_factory(1, 4, 2)
    # db.update_by_cell_info(c1)
    #
    c2 = db.get_cell_by_uk(c1)
    c2.raw_text = "123"
    db.update_by_id(c2)

    db.session.commit()
    pprint(db.list_all())
