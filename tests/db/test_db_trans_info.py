from pprint import pprint

import pytest

from mulaco.db.repo import TransInfoRepo
from mulaco.db.service import DbService
from mulaco.models.db_model import TransInfoPO


def trans_info_factory(cell_id, lang="jp"):
    return TransInfoPO(cell_id=cell_id, dst_lang=lang)


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
def test_trans_insert_one(db: TransInfoRepo):
    c1 = trans_info_factory(1, 4, 2)
    db.insert_one(c1)
    print(db.list_all())


@pytest.mark.skip()
def test_trans_insert_all(db: TransInfoRepo):
    c1 = trans_info_factory(1)
    c2 = trans_info_factory(2)
    c3 = trans_info_factory(3)
    c4 = trans_info_factory(4)
    db.insert_all([c1, c2, c3, c4])
    pprint(db.list_all())


def test_trans_update(db: TransInfoRepo):
    # 准备数据
    pprint(db.list_all())
    po1 = trans_info_factory(1, "ru")
    db.insert_one(po1)
    # 测试更新
    po2 = db.get_trans_by_uk(po1)
    po2.trans_text = "123"
    db.update_by_id(po2)
    db.session.commit()
    pprint(db.list_all())
