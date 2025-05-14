from pprint import pprint

import pytest

from mulaco.core.app import App
from mulaco.translate.helper import LocalDictCache


@pytest.fixture(scope="module")
def local_cli(app: App):
    return LocalDictCache(app)


def test_translate(local_cli: LocalDictCache):
    res = local_cli.api_translate_text("en", "zh", "hello, python")
    print(res)
