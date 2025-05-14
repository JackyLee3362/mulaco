import pytest

from mulaco.base.cache import JsonCache
from mulaco.base.config import TomlConfig
from mulaco.base.scaffold import Scaffold
from mulaco.core.app import App
from mulaco.db.service import DbService
from mulaco.models.bo_model import CellInfoBO, ExcelSheetBO, TransInfoBO
from mulaco.models.mapper import cell_bo_map_po, exsh_bo_map_po, trans_bo_map_po


@pytest.fixture(scope="session")
def config() -> TomlConfig:
    print("conftest 配置文件加载")
    config = TomlConfig("config/settings.toml")
    return config


@pytest.fixture(scope="session")
def mem() -> DbService:
    print("conftest 数据库配置 (memory) ")
    return DbService("sqlite:///:memory:")


@pytest.fixture(scope="session")
def mem_db_data() -> DbService:
    print("conftest 数据库配置 (memory) 包含测试数据 ")
    # 插入 exsh 表
    e1s1 = ExcelSheetBO(id=1, excel="ex1", sheet="sh1")
    e1s2 = ExcelSheetBO(id=2, excel="ex1", sheet="sh2")
    e2s1 = ExcelSheetBO(id=3, excel="ex2", sheet="sh1")
    # 插入数据
    c1 = CellInfoBO(id=1, row=4, col=2, src_lang="en", raw_text="你好", exsh_id=1)
    c2 = CellInfoBO(id=2, row=5, col=2, src_lang="en", raw_text="世界", exsh_id=1)
    c3 = CellInfoBO(id=3, row=5, col=2, src_lang="en", exsh_id=2)
    # 插入翻译
    t1zh = TransInfoBO(id=1, dst_lang="zh", trans_text="你好", cell_id=1)
    t2jp = TransInfoBO(id=2, dst_lang="jp", cell_id=2)

    # 数据库
    # TODO 传参应该是 BO 才对
    db = DbService("sqlite:///:memory:", True)
    # db.session.add_all([e1s1, e1s2, e2s1, c1, c2, c3, t1zh, t2jp])
    db.upsert_exsh(exsh_bo_map_po(e1s1))
    db.upsert_exsh(exsh_bo_map_po(e1s2))
    db.upsert_exsh(exsh_bo_map_po(e2s1))
    db.upsert_cell(cell_bo_map_po(c1))
    db.upsert_cell(cell_bo_map_po(c2))
    db.upsert_cell(cell_bo_map_po(c3))
    db.upsert_trans_info(trans_bo_map_po(t1zh))
    db.upsert_trans_info(trans_bo_map_po(t2jp))
    return db


@pytest.fixture(scope="session")
def db() -> DbService:
    print("conftest 数据库配置 (test.db) ")
    db = DbService("sqlite:///db/app.test.db", True)
    return db


@pytest.fixture(scope="session")
def cache() -> JsonCache:
    print("conftest 缓存配置 (cache.test.json)")
    cache = JsonCache("db/cache.test.json")
    return cache


# 应用骨架是会话级别的
@pytest.fixture(scope="session")
def scaffold() -> Scaffold:
    scaffold = Scaffold()
    scaffold.init_base()
    return scaffold


# 应用是会话级别的
@pytest.fixture(scope="session")
def app() -> App:
    app = App()
    app.init_base()
    app.init_app()
    return app
