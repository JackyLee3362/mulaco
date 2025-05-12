from pprint import pprint
import pytest
from mulaco.translate.cli import TencentCli


@pytest.fixture(scope="module")
def tencent_api(app):
    return TencentCli(app)


def test_1(tencent_api: TencentCli):
    res = tencent_api.api_translate_text("en", "zh", "hello, world")
    pprint(res)
