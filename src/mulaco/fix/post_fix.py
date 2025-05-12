# 翻译修复
import logging

from mulaco.core.app import App
from mulaco.models.bo_model import ExcelSheetBO
from mulaco.models.dto_model import ExcelDTO
from mulaco.models.po_model import TransInfoPO

log = logging.getLogger(__name__)


class ExcelPostFixer:

    def __init__(self, app: App):
        self.db = app.db
        self.cache = app.cache
        self.dst_langs = app.dst_langs

    def post_fix_excel(self, excel: ExcelDTO):
        ex_name = excel.excel_name
        for sheet in excel.sheets:
            sh_name = sheet.sheet_name
            bo = ExcelSheetBO(
                excel=excel.excel_name, sheet=sheet.sheet_name, header=sheet.header_row
            )
            # 获取所有没有处理过的 cell (sheet 层面)
            for dst in self.dst_langs:
                # TODO 配置 src
                res = self.db.get_all_not_processed_trans(bo, "en", dst, None)
                for ex_po, cell_po, trans_po in res:
                    trans_po: TransInfoPO
                    text = trans_po.trans_text
                    proc_text = self.process_trans_text(text)
                    trans_po.write_text = proc_text
                    self.db.upsert_trans_info(trans_po)

            log.debug(f"{ex_name}.{sh_name} 已经做好翻译后处理")

    def process_trans_text(self, text: str):
        return f"post({text})"
