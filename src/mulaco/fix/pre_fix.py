# 翻译修复
import logging

from mulaco.core.app import App
from mulaco.fix.parser import CellParser
from mulaco.models.bo_model import ExcelSheetBO
from mulaco.models.dto_model import ExcelDTO
from mulaco.models.po_model import CellInfoPO

log = logging.getLogger(__name__)


class ExcelPreFixer:

    def __init__(self, app: App):
        self.db = app.db
        self.cache = app.cache
        self.parser = CellParser()

    def pre_process_excel(self, excel: ExcelDTO):
        ex_name = excel.excel_name
        for sheet in excel.sheets:
            sh_name = sheet.sheet_name
            bo = ExcelSheetBO(
                excel=excel.excel_name,
                sheet=sheet.sheet_name,
                header=sheet.header_row,
            )
            # 获取所有没有处理过的 cell (sheet 层面)
            res = self.db.get_all_not_processed_cells(bo)
            for exsh_po, cell_po in res:
                # 提前存储数据
                cell_po: CellInfoPO
                text = cell_po.raw_text
                proc_text, info = self.parser.pre_parser(text)
                # 设置 cell
                cell_po.proc_text = proc_text
                if info:
                    cell_po.json = info
                self.db.upsert_cell(cell_po)
            log.debug(f"完成预处理 {ex_name}.{sh_name}")
