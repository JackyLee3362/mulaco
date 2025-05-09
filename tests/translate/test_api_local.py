import json
from pprint import pprint

from mulaco.base import AppBase
from mulaco.translate.api import LocalApi

my_dict = "config/dict.json"
app = AppBase()
app.setup()
cache = app.cache
local_api = LocalApi(cache)


def test_1():
    with open(my_dict, encoding="utf-8") as f:
        d = json.load(f)

    local_api.load_dict_glossary(d)
    ds = local_api.api_list_glossaries()
    pprint(ds)
