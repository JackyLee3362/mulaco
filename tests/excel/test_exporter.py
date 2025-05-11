from pprint import pprint

import pytest
import tomllib
from openpyxl import load_workbook

from mulaco.base import AppBase
from mulaco.base.settings import TomlConfig
from mulaco.db.service import DbService
from mulaco.excel.exporter import ExcelExporter
from mulaco.excel.loader import ExcelLoader
from mulaco.excel.model import BatchExcel, SheetDTO
from mulaco.translate.model import LanguagesConfig


@pytest.fixture(scope="module")
def handler():
    lang_model_path = "config/lang.toml"

    app_base = AppBase()
    app_base.setup()
    cache = app_base.cache

    db = DbService("sqlite:///db/test.db")

    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))
    lang_d = TomlConfig(lang_model_path)
    langs = LanguagesConfig.from_dict(lang_d.translate.model)

    # 更新 d

    eb = BatchExcel.from_dict(d)
    excel = eb.excels[0]

    exexporter = ExcelExporter(excel, db, cache)
    exexporter.setup_lang_config(langs)

    yield exexporter


# @pytest.mark.skip()
def test_handler_loader(handler: ExcelExporter):
    """手动构造并生成数据"""
    handler.export_excel()
