from pprint import pprint

import pytest

from mulaco.base.scaffold import Scaffold


@pytest.fixture(scope="module")
def app_base():
    app_base = Scaffold()
    yield app_base


def test_config(app_base: Scaffold):
    assert isinstance(app_base.config, dict)


def test_logger(app_base: Scaffold):
    import logging

    pprint(app_base.log_config)
    log = logging.getLogger("mulaco")
    assert 1 <= len(log.handlers) <= 2


def test_db(app_base: Scaffold):
    app_base.cache.set("hello", "世界")
    assert app_base.cache.get("hello") == "世界"
