import logging
import os

from mulaco.base.config import TomlConfig
from mulaco.base.scaffold import Scaffold
from mulaco.db.service import DbService
from mulaco.models.dto_model import BatchExcelDTO, LanguagesConfigDTO

log = logging.getLogger(__name__)


class App(Scaffold):

    def init_app(self):
        self.import_excel_config()
        self.import_dict()
        self.import_lang_path()
        self.init_db()

    def import_excel_config(self):
        """导入 excel 配置文件"""
        config_path = self.config.app.excel.excel_conf_url
        if not os.path.exists(config_path):
            raise FileNotFoundError("Excel 配置文件不存在，请检查")
        d = TomlConfig(config_path)
        self.batch_excels = BatchExcelDTO.from_dict(d)

    def import_lang_path(self):
        """导入 lang 配置文件"""
        config_path = self.config.app.translate.lang_conf_url
        if not os.path.exists(config_path):
            raise FileNotFoundError("语言配置文件不存在，请检查")
        d = TomlConfig(config_path)
        lang_conifg = LanguagesConfigDTO.from_dict(d.translate.model)
        self.langs_mapper = lang_conifg.langs
        self.dst_langs = sorted(
            lang_conifg.dst_langs, key=lambda x: self.langs_mapper[x].order
        )

    # TODO 现在就是必须要有这个配置，应该将其设置为可选项
    # 即没有这个文件也可以正常运行
    def import_dict(self):
        """导入用户自定义字典"""
        config_path = self.config.app.translate.dict_url
        if not os.path.exists(config_path):
            raise FileNotFoundError("语言配置文件不存在，请检查")
        user_dict = TomlConfig(config_path)
        self.user_dict = user_dict.dict

    def init_db(self):
        """初识化数据库"""
        url = self.config.app.db.url
        echo = self.config.app.db.echo
        self.db = DbService(url, echo)
