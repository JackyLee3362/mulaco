import pytest
import tomllib

from mulaco.base.scaffold import Scaffold
from mulaco.db.service import DbService
from mulaco.fix.pre_fix import ExcelPreFixer
from mulaco.models.config_model import BatchExcelVO


@pytest.fixture(scope="module")
def fixer() -> ExcelPreFixer:

    db = DbService("sqlite:///db/test.db")
    app = Scaffold()
    cache = app.cache

    fixer = ExcelPreFixer(db, cache)
    return fixer


def test_pre_fix(fixer: ExcelPreFixer):
    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))
    eb = BatchExcelVO.from_dict(d)
    excel = eb.excels[0]

    fixer.pre_fix_excel(excel)
