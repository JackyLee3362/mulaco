from pprint import pprint

from mulaco.base import AppBase
from mulaco.base.settings import TomlConfig
from mulaco.db.service import DbService
from mulaco.translate.cli import DeepLCli, MockCli, TencentCli
from mulaco.translate.model import LanguagesConfig
from mulaco.translate.service import TranslateService

lang_model_path = "config/lang.test.toml"
d = TomlConfig(lang_model_path)
langs_config = LanguagesConfig.from_dict(d.translate.model)

app = AppBase()
app.setup()
cache = app.cache

db = DbService("sqlite:///db/test.db")

deepl = DeepLCli(cache)
tencent = TencentCli(cache)
mockcli = MockCli(cache)

service = TranslateService(db, cache)
service.register_service(deepl)
service.register_service(tencent)
service.register_service(mockcli)
service.setup_lang_config(langs_config)


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
    pprint(d.translate.model)
    langs_config = LanguagesConfig.from_dict(d.translate.model)
    pprint(langs_config)
    #
    service.setup_lang_config(langs_config)
    pprint(service.dst_langs)
    pprint(service.lang_mapper)


def test_translate_lang():
    excel_name = "ClothingConfig.xlsx"
    src = "en"
    res = service.translate_excel_src(excel_name, src)
    pprint(res)
