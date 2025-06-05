# 一些复杂 sql 语句
from sqlalchemy import Select, select

from mulaco.models.bo_model import ExcelSheetBO
from mulaco.models.po_model import CellInfoPO, ExcelSheetPO, TransInfoPO


def build_sql_get_all_not_translated_cells(
    bo: ExcelSheetBO, src: str, dst: str = None, col: int = None
) -> Select:
    """获得【所有】【未翻译过】的 Cell"""
    stmt = (
        select(CellInfoPO)
        # 连接约束
        .join(ExcelSheetPO, ExcelSheetPO.id == CellInfoPO.exsh_id)
        # 左连接
        .outerjoin(
            TransInfoPO,
            # id 约束 + 目标语言约束，如果未翻译，则下面 TransInfoPO.id 是空的
            (CellInfoPO.id == TransInfoPO.cell_id) & (TransInfoPO.dst_lang == dst),
        )
        # exsh 约束
        .where(
            ExcelSheetPO.excel == bo.excel,
            ExcelSheetPO.sheet == bo.sheet,
        )
        # 业务约束
        # 筛选未翻译的字段
        .where(
            TransInfoPO.id.is_(None) | TransInfoPO.trans_text.is_(None),
            CellInfoPO.proc_text.isnot(None),
        )
        # delete 约束
        .where(
            ExcelSheetPO.is_delete.is_(False),
            CellInfoPO.is_delete.is_(False),
        ).order_by(CellInfoPO.row)
    )
    if src:
        stmt = stmt.where(CellInfoPO.src_lang == src)
    if col:
        stmt = stmt.where(CellInfoPO.col == col)
    return stmt


def build_sql_get_not_proc_cells(bo: ExcelSheetBO, src: str, col: int = None) -> Select:
    """获得【所有】【翻译过】但是【没有预处理】 的 Cell
    为什么返回两个对象：处理 Ref 可能需要 excel 和 sheet 信息
    """
    stmt = (
        # 返回结果
        select(ExcelSheetPO, CellInfoPO)
        # Inner Join 连接
        .join(ExcelSheetPO, ExcelSheetPO.id == CellInfoPO.exsh_id)
        # exsh 约束
        .where(
            ExcelSheetPO.excel == bo.excel,
            ExcelSheetPO.sheet == bo.sheet,
        )
        # 业务约束
        .where(
            CellInfoPO.raw_text.isnot(None),
            CellInfoPO.proc_text.is_(None),
        )
        # 删除约束
        .where(
            ExcelSheetPO.is_delete.is_(False),
            CellInfoPO.is_delete.is_(False),
        )
        # 排序
        .order_by(CellInfoPO.row)
    )
    # 参数约束
    if col:
        stmt = stmt.where(CellInfoPO.col == col)
    if src:
        stmt = stmt.where(CellInfoPO.src_lang == src)
    return stmt


def build_sql_get_all_not_proc_trans(
    bo: ExcelSheetBO, src: str = None, dst: str = None, col: int = None
) -> Select:
    stmt = (
        # 返回结果
        select(ExcelSheetPO, CellInfoPO, TransInfoPO)
        # Inner Join 连接
        .join(CellInfoPO, CellInfoPO.exsh_id == ExcelSheetPO.id).join(
            TransInfoPO, TransInfoPO.cell_id == CellInfoPO.id
        )
        # Exsh 约束
        .where(
            ExcelSheetPO.excel == bo.excel,
            ExcelSheetPO.sheet == bo.sheet,
        )
        # 业务约束
        .where(
            TransInfoPO.trans_text.isnot(None),
            TransInfoPO.write_text.is_(None),
        )
        # 删除约束
        .where(
            ExcelSheetPO.is_delete.is_(False),
            CellInfoPO.is_delete.is_(False),
        )
        # 排序
        .order_by(CellInfoPO.row)
    )
    # 参数约束
    if src:
        stmt = stmt.where(CellInfoPO.src_lang == src)
    if col:
        stmt = stmt.where(CellInfoPO.col == col)
    if dst:
        stmt = stmt.where(TransInfoPO.dst_lang == dst)
    return stmt


def build_sql_get_all_write_trans(
    bo: ExcelSheetBO, src: str, dst: str = None, col: int = None
) -> Select:
    """获取该 exsh 下所有的已经翻译过的结果"""
    stmt = (
        select(CellInfoPO, TransInfoPO)
        .join(ExcelSheetPO, ExcelSheetPO.id == CellInfoPO.exsh_id)
        .join(TransInfoPO, CellInfoPO.id == TransInfoPO.cell_id)
        .where(
            ExcelSheetPO.excel == bo.excel,
            ExcelSheetPO.sheet == bo.sheet,
            CellInfoPO.src_lang == src,
            TransInfoPO.write_text.isnot(None),
        )
        .where(
            ExcelSheetPO.is_delete.is_(False),
            CellInfoPO.is_delete.is_(False),
            TransInfoPO.is_delete.is_(False),
        )
    )
    # 参数约束
    if col:
        stmt = stmt.where(CellInfoPO.col == col)
    if dst:
        stmt = stmt.where(TransInfoPO.dst_lang == dst)
    return stmt
