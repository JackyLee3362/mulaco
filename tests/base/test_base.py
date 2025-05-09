from pprint import pprint

import pytest

from mulaco.base import AppBase


@pytest.fixture(scope="module")
def app_base():
    app_base = AppBase()
    app_base.setup()
    yield app_base


def test_config(app_base: AppBase):
    assert isinstance(app_base.config, dict)


def test_logger(app_base: AppBase):
    import logging

    pprint(app_base.log_config)
    log = logging.getLogger("mulaco")
    assert len(log.handlers) == 2


def test_db(app_base: AppBase):
    app_base.cache.set("hello", "世界")
    assert app_base.cache.get("hello") == "世界"
