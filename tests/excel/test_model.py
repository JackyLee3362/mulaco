import os
from pprint import pprint

from mulaco.base.config import TomlConfig
from mulaco.models.dto_model import (
    BatchExcelDTO,
    ExcelDTO,
    LanguagesConfigDTO,
    SheetDTO,
)


def test_load_config():
    d = TomlConfig("config/batch1.toml")
    pprint(d)


def test_map_dict():
    d = TomlConfig("config/batch1.toml")
    dto = BatchExcelDTO.from_dict(d)
    pprint(d)
    pprint(dto)


def test_map_dict_2():
    d = TomlConfig("config/batch1.toml")

    sheet = d.excels[0]["sheets"][0]
    SheetDTO.from_dict(sheet)

    excel = d.excels[0]
    pprint(excel)
    ExcelDTO.from_dict(excel)


def test_map_lang():

    d = TomlConfig("config/lang.test.toml")
    res = LanguagesConfigDTO.from_dict(d.translate.model)
    print(res)
