import pytest
import tomllib

from mulaco.base.scaffold import Scaffold
from mulaco.base.settings import TomlConfig
from mulaco.db.service import DbService
from mulaco.excel.exporter import ExcelExporter
from mulaco.models.config_model import BatchExcelVO, ExcelVO, LanguagesVO


@pytest.fixture(scope="module")
def app():
    return Scaffold()


@pytest.fixture(scope="module")
def handler(app: Scaffold):

    cache = app.cache

    db = DbService("sqlite:///db/test.db")

    # 传入更新后的数据
    exexporter = ExcelExporter(db, cache)

    lang_model_path = "config/lang.test.toml"
    lang_d = TomlConfig(lang_model_path)
    langs = LanguagesVO.from_dict(lang_d.translate.model)

    exexporter.setup_lang_config(langs)

    yield exexporter


# @pytest.mark.skip()
def test_handler_loader(app: Scaffold, handler: ExcelExporter):
    """手动构造并生成数据"""
    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))

    # 从 config 加载的数据
    eb = BatchExcelVO.from_dict(d)
    excel = eb.excels[0]

    # 从缓存中更新数据
    excel_d = ExcelVO.to_dict(excel)
    cache_d = app.cache.get(excel.excel_name, "excels")
    excel_d.update(cache_d)
    excel = ExcelVO.from_dict(excel_d)

    handler.export_excel(excel)
