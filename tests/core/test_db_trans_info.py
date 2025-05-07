from pprint import pprint

import pytest

from mulaco.core.db_models import TransInfo
from mulaco.core.repo import TransInfoRepo
from mulaco.core.service import DbService


def trans_info_factory(cell_id, lang="jp"):
    return TransInfo(cell_id=cell_id, dst_lang=lang)


@pytest.fixture(scope="module")
def db():
    cli = DbService("sqlite:///:memory:")
    db = TransInfoRepo(session=cli.session)
    c1 = trans_info_factory(1)
    c2 = trans_info_factory(2)
    c3 = trans_info_factory(3)
    c4 = trans_info_factory(4)
    db.insert_all([c1, c2, c3, c4])
    yield db


@pytest.mark.skip()
def test_cell_insert_one(db: TransInfoRepo):
    c1 = trans_info_factory(1, 4, 2)
    db.insert_one(c1)
    print(db.list())


@pytest.mark.skip()
def test_cell_insert_all(db: TransInfoRepo):
    c1 = trans_info_factory(1)
    c2 = trans_info_factory(2)
    c3 = trans_info_factory(3)
    c4 = trans_info_factory(4)
    db.insert_all([c1, c2, c3, c4])
    pprint(db.list())


def test_cell_update(db: TransInfoRepo):
    pprint(db.list())
    c1 = trans_info_factory(1, "ru")
    db.update_by_trans_info(c1)
    db.session.commit()
    pprint(db.list())
