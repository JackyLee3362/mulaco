import logging

from mulaco.base.console import console
from mulaco.core.app import App
from mulaco.excel.exporter import ExcelExporter
from mulaco.excel.loader import ExcelLoader
from mulaco.fix.post_fix import ExcelPostFixer
from mulaco.fix.pre_fix import ExcelPreFixer
from mulaco.translate.service import TranslateService

log = logging.getLogger(__name__)


class BatchService:
    def __init__(self, app: App):
        self.app = app
        self.db = app.db
        self.config = app.config
        self.cache = app.cache
        self.langs_mapper = app.langs_mapper
        self.dst_langs = app.dst_langs
        self.batch_excels = app.batch_excels
        # 设置 batch excel 配置

    # 所有步骤
    def batch_run(self):
        self.batch_load_excels()
        self.batch_pre_process_excels()
        self.batch_translate_excels()
        self.batch_post_fix_excels()
        self.batch_export_excels()

    # 第 1 步：加载数据
    def batch_load_excels(self):
        console.rule("加载数据")
        loader = ExcelLoader(self.app)
        log.info("开始批量加载 excel ...")
        for excel in self.batch_excels.excels:
            try:
                loader.load_excel(excel)
            except Exception:
                log.error(f"{excel.excel_name} 加载出错")
        log.info("完成批量加载 excel ...")

    # 第 2 步：预处理数据
    def batch_pre_process_excels(self):
        console.rule("数据预处理")
        log.info("开始批量预处理 excel 原始文本 ...")
        pre_fixer = ExcelPreFixer(self.app)
        for excel in self.batch_excels.excels:
            try:
                pre_fixer.pre_process_excel(excel)
            except Exception:
                log.error(f"批量预处理出错!!! {excel.excel_name} ")
        log.info("完成批量预处理 excel 原始文本 ...")

    # 第 3 步：翻译数据
    def batch_translate_excels(self):
        console.rule("翻译")
        log.info("开始批量翻译 excel  ...")
        trans_service = TranslateService(self.app)
        for excel in self.batch_excels.excels:
            try:
                trans_service.translate_excel(excel)
            except Exception:
                log.error(f"{excel.excel_name} 翻译出错")
        log.info("完成批量翻译 excels ...")

    # 第 4 步：修复翻译
    def batch_post_fix_excels(self):
        console.rule("数据后处理 - 修复翻译")
        log.info("开始批量修复翻译 excel 翻译 ...")
        # TODO 是否可以优化
        post_fixer = ExcelPostFixer(self.app)
        for excel in self.batch_excels.excels:
            try:
                post_fixer.post_fix_excel(excel)
            except Exception:
                log.error(f"批量修复翻译出错!!! {excel.excel_name}")
        log.info("完成批量修复翻译 excel 翻译 ...")

    # 第 5 步：导出数据
    def batch_export_excels(self):
        console.rule("导出")
        log.info("开始批量导出 excel ...")
        exporter = ExcelExporter(self.app)
        for excel in self.batch_excels.excels:
            try:
                exporter.export_excel(excel)
            except Exception:
                log.error(f"{excel.excel_name} 导出出错")
        log.info("完成批量导出 excel ...")
