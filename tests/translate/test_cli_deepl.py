import types
from pprint import pprint

from pytest_mock import MockerFixture

from mulaco.base.scaffold import Scaffold
from mulaco.translate.cli import DeepLCli

my_dict = "config/dict.json"
app = Scaffold()
cache = app.cache
deepl_api = DeepLCli(cache)


def test_translate():
    res = deepl_api.api_translate_text("en", "zh", "hello, world")
    pprint(res)


def test_2_create_glossary(mocker: MockerFixture):
    class MockRes: ...

    f = deepl_api.cli.create_glossary
    full_name = get_func_name(f)
    val = MockRes()
    val.glossary_id = "abc"
    # mocker.patch(full_name, return_value=val)
    res = deepl_api.api_create_glossary(
        "en", "zh", {"hello": "你~好~", "world": "世~界~"}
    )
    print(res)


def get_func_name(method):
    if not isinstance(method, (types.FunctionType, types.MethodType)):
        raise ValueError
    module_name = method.__module__
    # 获取方法的完全限定名（包括类名）
    qualified_name = method.__qualname__
    return f"{module_name}.{qualified_name}"


def test_2_list_sync():
    ds = deepl_api.api_list_glossaries(sync=True)
    for item in ds:
        print(item.glossary_id)


def test_get_glossary():
    deepl_api.api_get_glossary("en", "zh")


def test_3_del_glossary():
    deepl_api.api_delete_glossary("en", "zh")
