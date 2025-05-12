import logging
from pprint import pprint

import mulaco
from mulaco.base.scaffold import Scaffold


def test_config(scaffold: Scaffold):
    assert isinstance(scaffold.config, dict)


def test_logger(scaffold: Scaffold):
    pprint(scaffold.log_config)
    log = logging.getLogger(mulaco.__name__)
    assert 1 <= len(log.handlers) <= 2


def test_db(scaffold: Scaffold):
    scaffold.cache.set("hello", "世界")
    assert scaffold.cache.get("hello") == "世界"
