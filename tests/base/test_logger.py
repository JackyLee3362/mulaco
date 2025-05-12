import logging

from mulaco.base.config import TomlConfig
from mulaco.base.logger import set_logger

log = logging.getLogger(__name__)


def test_set_logger(config: TomlConfig):
    config.load_file("config/settings.test.toml")
    log.info("hello")
