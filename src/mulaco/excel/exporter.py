import logging
import shutil
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from mulaco.base.db import JsonCache
from mulaco.db.service import DbService
from mulaco.excel.utils import excel_col_alpha2num
from mulaco.models.business_model import ExcelSheetBO
from mulaco.models.config_model import ExcelVO, LanguagesVO, LanguageVO, SheetVO

log = logging.getLogger(__name__)


class ExcelExporter:
    CACHE_EXCEL_TBL = "excels"

    # TODO 这里的参数是传 excel_name 还是传 excel_dto 呢
    def __init__(self, db: DbService, cache: JsonCache):
        self.db = db
        self.cache = cache

    def setup_lang_config(self, langs_config: LanguagesVO):
        """配置待翻译语言
        TODO 感觉这里和 translate.service 中的代码重复，是否可以提取优化
        """
        self.dst_langs: list[str] = None
        self.lang_mapper: dict[str, LanguageVO] = {}
        dst_langs: list[LanguageVO] = []
        for lang in langs_config.langs:
            # 默认加入
            self.lang_mapper[lang.code] = lang
            # 如果激活该语言，则寻找对应服务
            if lang.active:
                dst_langs.append(lang)
        self.dst_langs = sorted(dst_langs, key=lambda x: x.offset)

    # -------------------- export --------------------
    def export_excel(self, excel: ExcelVO):
        if excel.skip:
            log.debug(f"{excel.excel_name} 跳过")
        try:
            # 第一步，复制数据
            self._copy_excel(excel)
            wb = load_workbook(excel.dst_path)
            for sheet_dto in excel.sheets:
                sheet = wb[sheet_dto.sheet_name]
                # 该参数写死，但是之后是可以配置的
                self.write_sheet(excel, sheet, sheet_dto, "en")

            # 保存
            wb.save(excel.dst_path)
        except Exception as e:
            log.error(f"{excel.excel_name} 写入数据时发送错误")
        finally:
            wb.close()

    def write_sheet(
        self, excel: ExcelVO, sheet: Worksheet, sheet_dto: SheetVO, src: str
    ):
        """TODO 优化建议，直接将准备好的数据批量写入"""
        # db 选择行
        ex_name = excel.excel_name
        sh_name = sheet_dto.sheet_name
        max_col = sheet_dto.max_col
        header_row = sheet_dto.header_row
        #
        exsh_bo = ExcelSheetBO(excel=ex_name, sheet=sh_name, header=None)
        cols = sheet_dto.lang_cols[src]
        total_dst_lang = len(self.dst_langs)
        for idx, src_col in enumerate(cols):
            # 主要是标记
            # idx 主要是标记序号的
            col_num = excel_col_alpha2num(src_col)
            for dst_lang_obj in self.dst_langs:
                # TODO 从 Lang 模型中提取 offset 或者，可以在设置 lang 时设置
                dst_code = dst_lang_obj.code
                offset = self.lang_mapper[dst_code].offset
                res = self.db.get_all_write_trans(exsh_bo, src, dst_code, col_num)
                # 计算列
                d_col = max_col + offset + total_dst_lang * idx
                # TODO 写入表头
                header_text = src_col + "列" + self.lang_mapper[dst_code].name
                sheet.cell(header_row, d_col).value = header_text

                for cell_po, trans_po in res:
                    c_row = cell_po.row
                    text = trans_po.write_text
                    sheet.cell(c_row, d_col).value = text
                log.debug(f"完成 {ex_name}.{sh_name} lang={dst_code} 中的写入")

    def _copy_excel(self, excel: ExcelVO):
        """复制文件到指定位置，如果存在，直接返回"""
        src = Path(excel.src_path)
        dst = Path(excel.dst_path)
        if dst.exists():
            return
        else:
            shutil.copy2(src, dst)
