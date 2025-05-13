from pprint import pprint

import pytest

from mulaco.core.app import App
from mulaco.translate.cli import LocalCli


@pytest.fixture(scope="module")
def local_cli(app: App):
    return LocalCli(app)


def test_my_dict(local_cli: LocalCli):
    pprint(local_cli.api_get_glossary("en", "zh"))


def test_translate(local_cli: LocalCli):
    res = local_cli.api_translate_text("en", "zh", "hello, python")
    print(res)
