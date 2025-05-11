from __future__ import annotations

from logging import getLogger

from mulaco.base.db import JsonCache
from mulaco.core.models import CellInfoBO, ExcelSheetBO, TransInfoBO
from mulaco.db.mapper import cell_po_map_bo, trans_bo_map_po
from mulaco.db.service import DbService as DbService
from mulaco.excel.model import ExcelDTO
from mulaco.excel.utils import excel_col_alpha2num
from mulaco.translate.cli import TranslateCli

from .model import Language, LanguagesConfig

log = getLogger(__name__)


class TranslateService:
    CACHE_EXCEL_TBL = "excels"

    def __init__(self, db: DbService, cache: JsonCache):
        self.db = db
        self.cache = cache
        self.api_services: dict[str, TranslateCli] = {}
        self.lang_mapper: dict[str, Language] = {}
        self.dst_langs: list[Language] = []

    def register_service(self, api: TranslateCli):
        self.api_services[api.name] = api

    def setup_lang_config(self, langs_config: LanguagesConfig):
        """配置待翻译语言"""
        dst_langs: list[Language] = []
        for lang in langs_config.langs:
            # 默认加入
            self.lang_mapper[lang.code] = lang
            # 如果激活该语言，则寻找对应服务
            if lang.active:
                name = lang.service_name
                lang.service = self.api_services[name]
                dst_langs.append(lang)
        self.dst_langs = sorted(dst_langs, key=lambda x: x.offset)

    def translate_excel_src(self, excel: str, src: str):
        d = self.cache.get(excel, self.CACHE_EXCEL_TBL)
        ex = ExcelDTO.from_dict(d)
        for dst_lang in self.dst_langs:
            dst = dst_lang.code
            for sheet in ex.sheets:
                exsh_bo = ExcelSheetBO(
                    ex.excel_name, sheet.sheet_name, header=sheet.header_row
                )
                cols = sheet.lang_cols[src]
                for col_alpha in cols:
                    col = excel_col_alpha2num(col_alpha)
                    self._translate_exsh_src(exsh_bo, src, dst, col)
                log.debug(f"已经翻译 {excel}.{sheet.sheet_name} 的 {col_alpha} 列")

    def _translate_exsh_src(self, exsh_bo: ExcelSheetBO, src: str, dst: str, col: int):
        """翻译 exsh"""
        # 获得所有已经翻译过的 trans
        all_cell_po = self.db.get_not_translated_cells(exsh_bo, src, dst, col)
        for cell_po in all_cell_po:
            text = cell_po.proc_text
            translated_text = self.translate_core(src, dst, text)
            trans_bo = TransInfoBO(
                dst_lang=dst,
                trans_text=translated_text,
                # TODO write_text 需要进一步处理，这里只是简化处理
                write_text=translated_text,
            )
            trans_po = trans_bo_map_po(trans_bo)
            trans_po.cell_id = cell_po.id

            self.db.upsert_trans_info(trans_po)

    def translate_core(self, src: str, dst: str, text: str):
        dst_lang = self.lang_mapper[dst]
        service: TranslateCli = dst_lang.service
        return service.api_translate_text(src, dst, text)
