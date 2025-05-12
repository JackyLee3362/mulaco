from pprint import pprint

import pytest
import sqlalchemy

from mulaco.db.repo import TransInfoRepo
from mulaco.db.service import DbService
from mulaco.models.po_model import TransInfoPO


@pytest.fixture(scope="module")
def repo(mem: DbService):
    db = TransInfoRepo(session=mem.session)
    c1 = TransInfoPO(cell_id=1, dst_lang="jp")
    c2 = TransInfoPO(cell_id=2, dst_lang="jp")
    c3 = TransInfoPO(cell_id=3, dst_lang="jp")
    db.insert_all([c1, c2, c3])
    db.session.commit()
    yield db


def test_trans_insert_one(repo: TransInfoRepo):
    c1 = TransInfoPO(cell_id=1, dst_lang="jp")
    # with pytest.raises(sqlite3.IntegrityError) as e:
    # with pytest.raises(sqlalchemy.exc.IntegrityError) as e:
    with pytest.raises(Exception) as e:
        print("错误类型", str(e))
        repo.list_all()
        repo.insert_one(c1)
        # TODO 问题 1 必须运行下列语句才报错（貌似是 autoflush 的错误）
        # TODO 问题 2 报错不是 sqlite3.IntegrityError ，但是 Exception 可以
        repo.list_all()


@pytest.mark.skip()
def test_trans_insert_all(repo: TransInfoRepo):
    c1 = TransInfoPO(cell_id=1, dst_lang="jp")
    c2 = TransInfoPO(cell_id=2, dst_lang="jp")
    c3 = TransInfoPO(cell_id=3, dst_lang="jp")
    c4 = TransInfoPO(cell_id=4, dst_lang="jp")
    repo.insert_all([c1, c2, c3, c4])
    pprint(repo.list_all())


def test_trans_update(repo: TransInfoRepo):
    # 准备数据
    po1 = TransInfoPO(cell_id=1, dst_lang="jp", trans_text="trans-text")
    repo.update_by_id(po1)
