import logging
import os
from pathlib import Path

from mulaco.base.config import TomlConfig
from mulaco.base.scaffold import Scaffold
from mulaco.db.service import DbService
from mulaco.excel.exporter import ExcelExporter
from mulaco.excel.loader import ExcelLoader
from mulaco.fix.post_fix import ExcelPostFixer
from mulaco.fix.pre_fix import ExcelPreFixer
from mulaco.models.dto_model import BatchExcelDTO, LanguageDTO, LanguagesConfigDTO
from mulaco.translate.service import TranslateService

log = logging.getLogger(__name__)


class ApiService:
    def __init__(self, db: DbService, app: Scaffold):
        self.db = db
        self.app = app
        self.config = app.config
        self.cache = app.cache
        # 设置 batch excel 配置

    def setup_lang_config(self, langs_config: LanguagesConfigDTO):
        """配置待翻译语言
        TODO 感觉这里和 translate.service 中的代码重复，是否可以提取优化
        """
        self.langs_config = langs_config
        self.dst_langs: list[str] = None
        self.lang_mapper: dict[str, LanguageDTO] = {}
        dst_langs: list[LanguageDTO] = []
        for lang in langs_config.langs:
            # 默认加入
            self.lang_mapper[lang.code] = lang
            # 如果激活该语言，则寻找对应服务
            if lang.active:
                dst_langs.append(lang)
        self.dst_langs = sorted(dst_langs, key=lambda x: x.order)

    def setup_batch_excel(self, excel_config: str | Path):
        if not os.path.exists(excel_config):
            raise FileNotFoundError("batch 配置文件不存在")
        d = TomlConfig(excel_config)
        self.batch_excel = BatchExcelDTO.from_dict(d)

    # 第 1 步：加载数据
    def api_load_excels(self):
        loader = ExcelLoader(self.db, self.cache)
        log.info("开始批量加载 excel ...")
        for excel in self.batch_excel.excels:
            try:
                loader.load_excel(excel)
            except Exception as e:
                log.error(f"{excel.excel_name} 加载出错")
        log.info("完成批量加载 excel ...")

    # 第 2 步：修复数据
    def api_pre_fix_excels(self):
        log.info("开始批量修复 excel 原始文本 ...")
        pre_fixer = ExcelPreFixer(self.db, self.cache)
        for excel in self.batch_excel.excels:
            try:
                pre_fixer.pre_fix_excel(excel)
            except Exception as e:
                log.error(f"{excel.excel_name} 修复原始文本出错")
        log.info("完成批量修复 excel 原始文本 ...")

    # 第 3 步：翻译数据
    def api_translate_excels(self):
        log.info("开始批量翻译 excel  ...")
        trans_service = TranslateService(self.db, self.cache)
        for excel in self.batch_excel.excels:
            # TODO 写死
            try:
                trans_service.translate_excel(excel, "en")
            except Exception as e:
                log.error(f"{excel.excel_name} 翻译出错")
        log.info("完成批量翻译 excels ...")

    # 第 4 步：修复翻译
    def api_post_fix_excels(self):
        log.info("开始批量修复 excel 翻译 ...")
        # TODO 是否可以优化
        post_fixer = ExcelPostFixer(self.db, self.cache)
        post_fixer.setup_lang_config(self.langs_config)
        for excel in self.batch_excel.excels:
            try:
                post_fixer.post_fix_excel(excel)
            except Exception as e:
                log.error(f"{excel.excel_name} 翻译修复出错")
        log.info("完成批量修复 excel 翻译 ...")

    # 第 5 步：导出数据
    def api_export_excels(self):
        log.info("开始批量导出 excel ...")
        exporter = ExcelExporter(self.db, self.cache)
        for excel in self.batch_excel.excels:
            try:
                exporter.export_excel(excel)
            except Exception as e:
                log.error(f"{excel.excel_name} 导出出错")
        log.info("完成批量导出 excel ...")
