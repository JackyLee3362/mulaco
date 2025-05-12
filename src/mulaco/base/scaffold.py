# __all__ = ["config", "base_db", "Base", "AppDbClient", "DbClientBase"]


from mulaco.base.constant import SETTING_FILE_PATH
from mulaco.base.db import JsonCache
from mulaco.base.logger import set_logger
from mulaco.base.settings import TomlConfig


class Scaffold:
    def __init__(self):
        # 初始化
        self.config = None
        self.log_config = None
        self.cache = None
        self.has_setup = False
        self.setup()

    def setup(self):
        # 只会初始化一次
        if not self.has_setup:
            self.setup_config()
            self.setup_logging()
            self.setup_base_db()
        self.has_setup = True

    def setup_config(self):
        # 初始配置
        try:
            self.config = TomlConfig()
            self.config.load_file(SETTING_FILE_PATH)
        except Exception as e:
            print(e)
            raise RuntimeError("配置文件错误")

    def setup_logging(self):
        # 日志配置
        try:
            root_module_name = __name__.split(".")[0]
            self.log_config = self.config.app.logging
            set_logger(root_module_name, **self.log_config)
        except Exception as e:
            print(e)
            raise RuntimeError("日志配置错误")

    def setup_base_db(self):
        # 数据库配置
        try:
            self.cache = JsonCache(db_url=self.config.app.cache.url)
        except Exception as e:
            print(e)
            raise RuntimeError("数据库配置错误")
