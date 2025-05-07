import logging

import mulaco.base.logger

log = logging.getLogger(__name__)


def test_logger_1():
    print("nihao")
    log.info("hello")
    log.info("hello")
