from mulaco.base.cache import JsonCache
from mulaco.base.config import TomlConfig
from mulaco.base.console import console
from mulaco.base.constant import (
    ENV,
    SETTING_ENV_FILE_PATH,
    SETTINGS_DEFAULT_PATH,
    init_path_dir,
)
from mulaco.base.logger import set_logger

# __all__ = ["config", "base_db", "Base", "AppDbClient", "DbClientBase"]


class Scaffold:
    def __init__(self):
        # 初始化
        self.config = None
        self.log_config = None
        self.cache = None

    def init_base(self):
        console.print(f"当前环境: {ENV}")
        init_path_dir()
        self.init_config()
        self.init_logging()
        self.init_cache()

    def init_config(self):
        # 初始配置
        self.config = TomlConfig()
        self.config.load_file(SETTINGS_DEFAULT_PATH)
        if ENV:
            self.config.load_file(SETTING_ENV_FILE_PATH)

    def init_logging(self):
        # 日志配置
        root_module_name = __name__.split(".")[0]
        self.log_config = self.config.app.logging
        set_logger(root_module_name, **self.log_config)

    def init_cache(self):
        # 数据库配置
        self.cache = JsonCache(cache_url=self.config.app.cache.url)

    def close_cache(self):
        """关闭缓存"""
        self.cache.close()
