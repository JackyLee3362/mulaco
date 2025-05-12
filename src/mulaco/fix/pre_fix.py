# 翻译修复
import logging

from mulaco.base.db import JsonCache
from mulaco.db.service import DbService
from mulaco.models.business_model import ExcelSheetBO
from mulaco.models.config_model import ExcelVO
from mulaco.models.db_model import CellInfoPO

log = logging.getLogger(__name__)


class ExcelPreFixer:

    def __init__(self, db: DbService, cache: JsonCache):
        self.db = db
        self.cache = cache

    def pre_fix_excel(self, excel: ExcelVO):
        ex_name = excel.excel_name
        for sheet in excel.sheets:
            sh_name = sheet.sheet_name
            bo = ExcelSheetBO(
                excel.excel_name, sheet=sheet.sheet_name, header=sheet.header_row
            )
            # 获取所有没有处理过的 cell (sheet 层面)
            res = self.db.get_all_not_processed_cells(bo, "en", None)
            for exsh_po, cell_po in res:
                # 提前存储数据
                cell_po: CellInfoPO
                text = cell_po.raw_text
                proc_text = self._process_raw_text(text)
                # 设置 cell
                cell_po.proc_text = proc_text
                self.db.upsert_cell(cell_po)
            log.debug(f"{ex_name}.{sh_name} 已经做好文本预处理")

    # TODO 转换为 raw_text
    def _process_raw_text(self, text: str):
        return f"pre({text})"
