from pprint import pprint

from mulaco.base.config import TomlConfig
from mulaco.models.dto_model import LanguageDTO, LanguagesConfigDTO

lang_model_path = "config/lang.toml"


def test_load_lang_model():
    d = TomlConfig(lang_model_path)
    pprint(d.translate.model.langs[0])
    lang_zh = LanguageDTO.from_dict(d.translate.model.langs[0])
    pprint(lang_zh)


def test_load_lang_config():
    d = TomlConfig(lang_model_path)
    pprint(d.translate.model)
    langs = LanguagesConfigDTO.from_dict(d.translate.model)
    pprint(langs)
