# 翻译修复
import logging

from mulaco.base.db import JsonCache
from mulaco.db.service import DbService
from mulaco.models.business_model import ExcelSheetBO
from mulaco.models.config_model import ExcelVO, LanguagesVO, LanguageVO
from mulaco.models.db_model import TransInfoPO

log = logging.getLogger(__name__)


class ExcelPostFixer:

    def __init__(self, db: DbService, cache: JsonCache):
        self.db = db
        self.cache = cache

    def setup_lang_config(self, langs_config: LanguagesVO):
        """配置待翻译语言
        TODO 感觉这里和 translate.service 中的代码重复，是否可以提取优化
        """
        self.lang_mapper: dict[str, LanguageVO] = {}
        dst_langs: list[LanguageVO] = []
        for lang in langs_config.langs:
            # 默认加入
            self.lang_mapper[lang.code] = lang
            # 如果激活该语言，则寻找对应服务
            if lang.active:
                dst_langs.append(lang)
        self.dst_langs = sorted(dst_langs, key=lambda x: x.offset)

    def post_fix_excel(self, excel: ExcelVO):
        ex_name = excel.excel_name
        for sheet in excel.sheets:
            sh_name = sheet.sheet_name
            bo = ExcelSheetBO(
                excel.excel_name, sheet=sheet.sheet_name, header=sheet.header_row
            )
            # 获取所有没有处理过的 cell (sheet 层面)
            for dst_lang_obj in self.dst_langs:
                dst_code = dst_lang_obj.code
                # TODO 配置 src
                res = self.db.get_all_not_processed_trans(bo, "en", dst_code, None)
                for ex_po, cell_po, trans_po in res:
                    trans_po: TransInfoPO
                    text = trans_po.trans_text
                    proc_text = self.process_trans_text(text)
                    trans_po.write_text = proc_text
                    self.db.upsert_trans_info(trans_po)

            log.debug(f"{ex_name}.{sh_name} 已经做好翻译后处理")

    def process_trans_text(self, text: str):
        return f"post({text})"
