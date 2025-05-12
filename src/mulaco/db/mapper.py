from mulaco.models.business_model import CellInfoBO, ExcelSheetBO, TransInfoBO
from mulaco.models.db_model import CellInfoPO, ExcelSheetPO, TransInfoPO


def exsh_bo_map_po(bo: ExcelSheetBO) -> ExcelSheetPO:
    return ExcelSheetPO(excel=bo.excel, sheet=bo.sheet, header=bo.header)


def exsh_po_map_bo(po: ExcelSheetPO) -> ExcelSheetBO:
    return ExcelSheetBO(po.excel, po.sheet, po.header)


def cell_bo_map_po(bo: CellInfoBO) -> CellInfoPO:
    return CellInfoPO(
        row=bo.row,
        col=bo.col,
        src_lang=bo.src_lang,
        raw_text=bo.raw_text,
        proc_text=bo.proc_text,
    )


def cell_po_map_bo(po: CellInfoPO) -> CellInfoBO:
    return CellInfoBO(
        row=po.row,
        col=po.col,
        src_lang=po.src_lang,
        raw_text=po.raw_text,
        proc_text=po.proc_text,
    )


def trans_bo_map_po(bo: TransInfoBO) -> TransInfoPO:
    return TransInfoPO(
        dst_lang=bo.dst_lang, trans_text=bo.trans_text, write_text=bo.write_text
    )


def trans_po_map_bo(po: TransInfoPO) -> TransInfoBO:
    return TransInfoBO(
        dst_lang=po.dst_lang, trans_text=po.trans_text, write_text=po.write_text
    )
