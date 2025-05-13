# 翻译修复
import logging

from mulaco.core.app import App
from mulaco.fix.parser import CellParser
from mulaco.models.bo_model import ExcelSheetBO
from mulaco.models.dto_model import ExcelDTO
from mulaco.models.po_model import TransInfoPO

log = logging.getLogger(__name__)


class ExcelPostFixer:
    EXCELS_TBL = "excels"
    ref_max_col_key = "ref-max-col"

    def __init__(self, app: App):
        self.db = app.db
        self.cache = app.cache
        self.dst_langs = app.dst_langs
        self.langs_mapper = app.langs_mapper
        self.parser = CellParser()

    def post_fix_excel(self, excel: ExcelDTO):
        ex_name = excel.excel_name
        cur_excel_cache = self.cache.get(ex_name, self.EXCELS_TBL)
        ref_excel_names = cur_excel_cache.get("refs", [])
        # 提前拿出 ref 信息
        ref_dtos = []
        # TODO 目前只支持单张表
        for ref_name in ref_excel_names:
            ref_name = ref_excel_names[0]
            ref_ex = self.cache.get(ref_name, self.EXCELS_TBL)
            ref_dto = ExcelDTO.from_dict(ref_ex)
            ref_dtos.append(ref_dto)

        log.debug(f"表 {ex_name} 翻译后处理开始")
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
                    info = cell_po.json
                    order = self.langs_mapper[dst].order
                    total = len(self.dst_langs)
                    proc_text = self.parser.post_parser(
                        text, info, ref_dtos, order, total
                    )
                    trans_po.write_text = proc_text
                    self.db.upsert_trans_info(trans_po)
                log.debug(f"表 {sh_name} 列 {dst} 翻译后处理完成")
        log.debug(f"表 {ex_name} 翻译后处理完成")
