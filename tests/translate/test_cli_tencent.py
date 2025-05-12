from pprint import pprint

from mulaco.base.scaffold import Scaffold
from mulaco.translate.cli import TencentCli

my_dict = "config/dict.json"
app = Scaffold()
cache = app.cache
tencent_api = TencentCli(cache)


def test_1():
    res = tencent_api.api_translate_text("en", "zh", "hello, world")
    pprint(res)
