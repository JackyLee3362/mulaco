from __future__ import annotations

from logging import getLogger

from mulaco.base.db import JsonCache
from mulaco.core.app import App
from mulaco.db.service import DbService as DbService
from mulaco.excel.utils import excel_col_alpha2num
from mulaco.models.bo_model import ExcelSheetBO, TransInfoBO
from mulaco.models.dto_model import ExcelDTO, LanguageDTO
from mulaco.models.mapper import trans_bo_map_po
from mulaco.translate.cli import TranslateCli

from ..models.dto_model import LanguagesConfigDTO

log = getLogger(__name__)


class TranslateService:
    CACHE_EXCEL_TBL = "excels"

    def __init__(self, app: App):
        self.app = app
        self.db = app.db
        self.cache = app.cache
        self.langs_mapper: dict[str, LanguageDTO] = app.langs_mapper
        self.dst_langs: list[LanguageDTO] = app.dst_langs
        self.api_services: dict[str, TranslateCli] = {}

    def register_service(self, api: TranslateCli):
        self.api_services[api.name] = api

    def map_lang_with_service(self):
        """配置待翻译语言"""
        for k, v in self.app.langs_mapper.items():
            if v.active:
                name = v.service_name
                v.service = self.api_services[name]

    def translate_excel(self, excel: ExcelDTO, src: str):
        for dst_lang in self.dst_langs:
            for sheet in excel.sheets:
                exsh_bo = ExcelSheetBO(
                    excel=excel.excel_name,
                    sheet=sheet.sheet_name,
                    header=sheet.header_row,
                )
                cols = sheet.lang_cols[src]
                for col_alpha in cols:
                    col = excel_col_alpha2num(col_alpha)
                    self._translate_exsh_src(exsh_bo, src, dst_lang, col)
                log.debug(
                    f"已经翻译 {excel.excel_name}.{sheet.sheet_name} 的 {col_alpha} 列 {src}-> {dst_lang}"
                )

    def _translate_exsh_src(self, exsh_bo: ExcelSheetBO, src: str, dst: str, col: int):
        """翻译 exsh"""
        # 获得所有已经翻译过的 trans
        all_cell_po = self.db.get_not_translated_cells(exsh_bo, src, dst, col)
        for cell_po in all_cell_po:
            text = cell_po.proc_text
            translated_text = self._translate_core(src, dst, text)
            trans_bo = TransInfoBO(
                dst_lang=dst,
                trans_text=translated_text,
            )
            trans_po = trans_bo_map_po(trans_bo)
            trans_po.cell_id = cell_po.id

            self.db.upsert_trans_info(trans_po)

    def _translate_core(self, src: str, dst: str, text: str):
        dst_lang = self.langs_mapper[dst]
        service: TranslateCli = dst_lang.service
        return service.api_translate_text(src, dst, text)
