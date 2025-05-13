import pytest

from mulaco.core.app import App
from mulaco.translate.service import TranslateService


@pytest.fixture(scope="module")
def trans_service(app: App):
    return TranslateService(app)


def test_翻译服务翻译_excel(app: App, trans_service: TranslateService):
    excel = app.batch_excels.excels[0]
    trans_service.translate_excel(excel)
