from pprint import pprint

import pytest

from mulaco.translate.cli import DeepLCli


@pytest.fixture(scope="module")
def deepl_cli(app):
    return DeepLCli(app)


def test_translate(deepl_cli: DeepLCli):
    res = deepl_cli.api_translate_text("en", "zh", "hello, world")
    print(res)
    assert "hello" not in res
    assert "world" not in res


def test_get_glossary(deepl_cli: DeepLCli):
    pprint(deepl_cli._get_glossary("en", "zh"))


def test_get_all_glossary(deepl_cli: DeepLCli):
    pprint(deepl_cli.cli.list_glossaries())


def test_1_普通翻译(tencent_api: DeepLCli):
    res = tencent_api.api_translate_text("en", "zh", "good morning!")
    pprint(res)


def test_2_标签翻译_1_普通标签_无字典缓存(tencent_api: DeepLCli):
    res = tencent_api.api_translate_text("en", "zh", "<dev>good</dev> morning!")
    pprint(res)


def test_2_标签翻译_2(tencent_api: DeepLCli):
    res = tencent_api.api_translate_text("en", "zh", "<dev>hello</dev>, world")
    pprint(res)


def test_2_标签翻译_3(tencent_api: DeepLCli):
    res = tencent_api.api_translate_text("en", "zh", "<hello>hello</hello>, world")
    pprint(res)
