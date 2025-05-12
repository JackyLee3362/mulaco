import pytest

from mulaco.core.app import App
from mulaco.fix.post_fix import ExcelPostFixer


@pytest.fixture(scope="module")
def post_fixer(app):
    return ExcelPostFixer(app)


def test_post_fix(app: App, post_fixer: ExcelPostFixer):
    post_fixer.post_fix_excel(app.batch_excels.excels[0])
