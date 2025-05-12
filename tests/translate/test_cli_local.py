from pprint import pprint

import pytest

from mulaco.core.app import App
from mulaco.translate.cli import LocalCli


@pytest.fixture(scope="module")
def local_cli(app: App):
    return LocalCli(app)


def test_my_dict(app, local_cli: LocalCli):
    d = app.user_dict
    local_cli.load_dict_glossary(d)
    ds = local_cli.api_list_glossaries()
    pprint(ds)
