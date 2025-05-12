import pytest

from mulaco.core.app import App
from mulaco.translate.cli import DeepLCli, MockCli, TencentCli
from mulaco.translate.service import TranslateService


@pytest.fixture(scope="module")
def trans_service(app: App):
    deepl = DeepLCli(app)
    tencent = TencentCli(app)
    mockcli = MockCli(app)
    service = TranslateService(app)
    service.register_service(deepl)
    service.register_service(tencent)
    service.register_service(mockcli)
    service.map_lang_with_service()
    return service


def test_翻译服务翻译_excel(app: App, trans_service: TranslateService):
    excel = app.batch_excels.excels[0]
    trans_service.translate_excel(excel, "en")
