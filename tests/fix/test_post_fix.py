import pytest
import tomllib

from mulaco.base.scaffold import Scaffold
from mulaco.base.settings import TomlConfig
from mulaco.db.service import DbService
from mulaco.fix.post_fix import ExcelPostFixer
from mulaco.models.config_model import BatchExcelVO, ExcelVO, LanguagesVO


@pytest.fixture(scope="module")
def fixer() -> ExcelPostFixer:

    db = DbService("sqlite:///db/test.db")
    app = Scaffold()
    cache = app.cache

    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))

    # 从 config 加载的数据
    eb = BatchExcelVO.from_dict(d)
    excel = eb.excels[0]

    # 从缓存中更新数据
    excel_d = ExcelVO.to_dict(excel)
    cache_d = cache.get(excel.excel_name, "excels")
    excel_d.update(cache_d)
    excel = ExcelVO.from_dict(excel_d)

    fixer = ExcelPostFixer(db, cache)
    lang_model_path = "config/lang.test.toml"
    lang_d = TomlConfig(lang_model_path)
    langs_conf = LanguagesVO.from_dict(lang_d.translate.model)
    fixer.setup_lang_config(langs_conf)
    return fixer


def test_post_fix(fixer: ExcelPostFixer):
    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))
    eb = BatchExcelVO.from_dict(d)
    excel = eb.excels[0]

    fixer.post_fix_excel(excel)
