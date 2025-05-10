from pprint import pprint

from mulaco.base import AppBase
from mulaco.translate.api import TencentApi

my_dict = "config/dict.json"
app = AppBase()
app.setup()
cache = app.cache
tencent_api = TencentApi(cache)


def test_1():
    res = tencent_api.api_translate_text("en", "zh", "hello, world")
    pprint(res)
