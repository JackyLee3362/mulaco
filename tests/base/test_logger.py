import logging

from mulaco.base.config import TomlConfig

log = logging.getLogger(__name__)


def test_set_logger(config: TomlConfig):
    config.load_file("config/settings.toml")
    log.info("hello")
