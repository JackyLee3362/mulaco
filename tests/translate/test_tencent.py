from pprint import pprint

import pytest

from mulaco.translate.translator import TencentTranslator


@pytest.fixture(scope="module")
def tencent_api(app):
    return TencentTranslator(app)


def test_1_普通翻译(tencent_api: TencentTranslator):
    res = tencent_api.api_translate_text("en", "zh", "good morning!")
    # pprint(res)


def test_2_标签翻译_1_普通标签_无字典缓存(tencent_api: TencentTranslator):
    res = tencent_api.api_translate_text("en", "zh", "<dev>good</dev> morning!")
    # pprint(res)


def test_2_标签翻译_2(tencent_api: TencentTranslator):
    res = tencent_api.api_translate_text("en", "zh", "<dev>hello</dev>, world")
    # pprint(res)


def test_2_标签翻译_3(tencent_api: TencentTranslator):
    res = tencent_api.api_translate_text("en", "zh", "<hello>hello</hello>, world")
    # pprint(res)
