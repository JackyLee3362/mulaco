from pprint import pprint

import tomllib

from mulaco.base.scaffold import Scaffold
from mulaco.base.settings import TomlConfig
from mulaco.db.service import DbService
from mulaco.models.config_model import BatchExcelVO, ExcelVO, LanguagesVO
from mulaco.translate.cli import DeepLCli, MockCli, TencentCli
from mulaco.translate.service import TranslateService

lang_model_path = "config/lang.test.toml"
d = TomlConfig(lang_model_path)
langs_config = LanguagesVO.from_dict(d.translate.model)

app = Scaffold()
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
    langs_config = LanguagesVO.from_dict(d.translate.model)
    pprint(langs_config)
    #
    service.setup_lang_config(langs_config)
    pprint(service.dst_langs)
    pprint(service.lang_mapper)


def test_translate_lang():
    config_file = "config/batch1.toml"
    d = tomllib.load(open(config_file, "rb"))

    # 从 config 加载的数据
    eb = BatchExcelVO.from_dict(d)
    excel_dto = eb.excels[0]

    # 从缓存中更新数据
    excel_d = ExcelVO.to_dict(excel_dto)
    cache_d = app.cache.get(excel_dto.excel_name, "excels")
    excel_d.update(cache_d)
    excel_dto = ExcelVO.from_dict(excel_d)
    res = service.translate_excel(excel_dto, "en")
    pprint(res)
