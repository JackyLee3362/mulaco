import pytest

from mulaco.core.app import App
from mulaco.excel.loader import ExcelLoader


@pytest.fixture(scope="module")
def loader(app):
    return ExcelLoader(app)


def test_loader_load(app: App, loader: ExcelLoader):
    excel = app.batch_excels.excels[0]
    loader.load_excel(excel)
