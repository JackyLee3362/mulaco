from pprint import pprint

from mulaco.base.settings import TomlConfig
from mulaco.translate.model import Language, LanguagesConfig

lang_model_path = "config/lang.toml"


def test_load_lang_model():
    d = TomlConfig(lang_model_path)
    pprint(d.translate.model.langs[0])
    lang_zh = Language.from_dict(d.translate.model.langs[0])
    pprint(lang_zh)


def test_load_lang_config():
    d = TomlConfig(lang_model_path)
    pprint(d.translate.model)
    langs = LanguagesConfig.from_dict(d.translate.model)
    pprint(langs)
