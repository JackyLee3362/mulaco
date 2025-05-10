from pprint import pprint

import tomllib

from mulaco.base import AppBase
from mulaco.translate.api import LocalApi

my_dict = "config/dict.toml"
app = AppBase()
app.setup()
cache = app.cache
local_api = LocalApi(cache)


def test_my_dict():
    d = tomllib.load(open(my_dict, "rb"))
    local_api.load_dict_glossary(d)
    ds = local_api.api_list_glossaries()
    pprint(ds)
