from pprint import pprint

import tomllib

from mulaco.base.scaffold import Scaffold
from mulaco.translate.cli import LocalCli

my_dict = "config/dict.toml"
app = Scaffold()
cache = app.cache
local_api = LocalCli(cache)


def test_my_dict():
    d = tomllib.load(open(my_dict, "rb"))
    local_api.load_dict_glossary(d)
    ds = local_api.api_list_glossaries()
    pprint(ds)
