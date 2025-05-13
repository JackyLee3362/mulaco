from pprint import pprint

import pytest

from mulaco.base.config import TomlConfig
from mulaco.base.scaffold import Scaffold
from mulaco.db.service import DbService
from mulaco.models.dto_model import BatchExcelDTO, ExcelDTO, LanguagesConfigDTO
from mulaco.translate.cli import DeepLCli, MockCli, TencentCli
from mulaco.translate.service import TranslateService


@pytest.fixture
def mock_cli():
    pass


def test_translate_lang():
    pass
