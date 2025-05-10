from pprint import pprint

from mulaco.base import AppBase
from mulaco.base.settings import TomlConfig
from mulaco.db.service import DbService
from mulaco.translate.cli import DeepLCli, TencentCli
from mulaco.translate.model import LanguagesConfig
from mulaco.translate.service import TranslateService

lang_model_path = "config/lang.toml"
d = TomlConfig(lang_model_path)
langs_config = LanguagesConfig.from_dict(d.translate.model)

app = AppBase()
app.setup()

db = DbService("sqlite:///:memory:")

service = TranslateService(db, app.cache)
deepl = DeepLCli(app.cache)
tencent = TencentCli(app.cache)


def test_1_register_service():
    """测试 api 注册服务"""
    service.register_service(deepl)
    service.register_service(tencent)
    pprint(service.api_services)
    assert len(service.api_services) == 2


def test_2_setup_languages():
    """测试 lang 注册服务"""
    service.register_service(deepl)
    service.register_service(tencent)
    # 装配 lang
    d = TomlConfig(lang_model_path)
    pprint(d.translate.model)
    langs_config = LanguagesConfig.from_dict(d.translate.model)
    pprint(langs_config)
    #
    service.setup_config(langs_config)
    pprint(service.dst_langs)
    pprint(service.lang_mapper)


def test_translate_lang():
    service
    pass
