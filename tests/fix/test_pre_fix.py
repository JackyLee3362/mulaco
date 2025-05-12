import pytest

from mulaco.core.app import App
from mulaco.fix.pre_fix import ExcelPreFixer


@pytest.fixture(scope="module")
def pre_fixer(app):
    return ExcelPreFixer(app)


def test_pre_fix(app: App, pre_fixer: ExcelPreFixer):
    pre_fixer.pre_fix_excel(app.batch_excels.excels[0])
