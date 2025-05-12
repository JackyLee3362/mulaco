import pytest

from mulaco.core.app import App
from mulaco.excel.exporter import ExcelExporter


@pytest.fixture(scope="module")
def exporter(app: App):
    exporter = ExcelExporter(app)
    yield exporter


# @pytest.mark.skip()
def test_handler_loader(app: App, exporter: ExcelExporter):
    exporter.export_excel(app.batch_excels.excels[0])
