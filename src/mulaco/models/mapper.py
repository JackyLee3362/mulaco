from mulaco.models.bo_model import CellInfoBO, ExcelSheetBO, TransInfoBO
from mulaco.models.po_model import CellInfoPO, ExcelSheetPO, TransInfoPO


def exsh_bo_map_po(bo: ExcelSheetBO) -> ExcelSheetPO:
    return ExcelSheetPO(
        id=bo.id,
        excel=bo.excel,
        sheet=bo.sheet,
        header=bo.header,
    )


def exsh_po_map_bo(po: ExcelSheetPO) -> ExcelSheetBO:
    return ExcelSheetBO(
        id=po.id,
        excel=po.excel,
        sheet=po.sheet,
        header=po.header,
    )


def cell_bo_map_po(bo: CellInfoBO) -> CellInfoPO:
    return CellInfoPO(
        id=bo.id,
        row=bo.row,
        col=bo.col,
        src_lang=bo.src_lang,
        raw_text=bo.raw_text,
        proc_text=bo.proc_text,
        exsh_id=bo.exsh_id,
    )


def cell_po_map_bo(po: CellInfoPO) -> CellInfoBO:
    return CellInfoBO(
        id=po.id,
        row=po.row,
        col=po.col,
        src_lang=po.src_lang,
        raw_text=po.raw_text,
        proc_text=po.proc_text,
        exsh_id=po.exsh_id,
    )


def trans_bo_map_po(bo: TransInfoBO) -> TransInfoPO:
    return TransInfoPO(
        id=bo.id,
        dst_lang=bo.dst_lang,
        trans_text=bo.trans_text,
        write_text=bo.write_text,
        cell_id=bo.cell_id,
    )


def trans_po_map_bo(po: TransInfoPO) -> TransInfoBO:
    return TransInfoBO(
        id=po.id,
        dst_lang=po.dst_lang,
        trans_text=po.trans_text,
        write_text=po.write_text,
        cell_id=po.cell_id,
    )
