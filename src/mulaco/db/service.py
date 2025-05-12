import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from mulaco.db.repo import CellInfoRepo, ExcelSheetRepo, TransInfoRepo
from mulaco.db.sql import (
    build_sql_get_all_not_proc_trans,
    build_sql_get_all_not_translated_cells,
    build_sql_get_all_write_trans,
    build_sql_get_not_proc_cells,
)
from mulaco.models.bo_model import ExcelSheetBO, TransInfoBO
from mulaco.models.mapper import exsh_bo_map_po
from mulaco.models.po_model import Base, CellInfoPO, ExcelSheetPO, TransInfoPO

log = logging.getLogger(__name__)


class DbService:
    """数据库服务"""

    def __init__(self, db_url: str, echo=False) -> None:
        """连接 + 设置数据库"""
        self.engine = create_engine(db_url, echo=echo)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.setup_repo()

    def setup_repo(self) -> None:
        """初始设置"""
        self.exsh_repo = ExcelSheetRepo(self.session)
        self.cell_repo = CellInfoRepo(self.session)
        self.trans_repo = TransInfoRepo(self.session)

    # --------------------------  Exsh  --------------------------

    def get_exsh_by_name(self, excel: str, sheet: str) -> ExcelSheetPO:
        """根据 excel 名字 + sheet 名字获得 exsh 对象(记录)"""
        return self.exsh_repo.get_exsh_by_uk(excel, sheet)

    def get_all_exsh(self) -> list[ExcelSheetPO]:
        """获得所有数据库中的 exsh 对象(记录)"""
        return self.exsh_repo.list_all()

    # TODO 待优化
    # TODO 待测试
    def delete_exsh(self, record: TransInfoBO) -> None:
        """软删除数据库中的 exsh 对象(记录)"""
        try:
            exsh = self.get_exsh_by_name(record)
            # 删除 excels
            exsh.is_delete = True
            self.exsh_repo.update_by_id(exsh)

            # 删除所有 cells
            self.cell_repo.batch_delete_by_exid(exsh.id)
            cells = self.cell_repo.get_list_by_cond((CellInfoPO.exsh_id == exsh.id))

            # 删除所有 trans
            for cell in cells:
                self.trans_repo.batch_delete_by_cell_id(cell.id)
            self.session.commit()
        except Exception:
            log.error("删除 excel sheet 错误")
            # log.exception(e)
            self.session.rollback()

    # TODO 其实入参应该是 DTO，返回结果也是 DTO
    # 且 DTO 在设计时应该有 id
    # 我的里面是没有的，所以需要改进
    def upsert_exsh(self, po: ExcelSheetPO) -> int:
        try:
            # po = exsh_bo_map_po(po)
            old_po = self.exsh_repo.get_exsh_by_uk(po.excel, po.sheet)
            # 更新
            if old_po:
                po.id = old_po.id
                new_po = self.exsh_repo.update_by_id(po)
            # 新增
            else:
                new_po = self.exsh_repo.insert_one(po)
            self.session.commit()
            return new_po.id
        except Exception:
            # log.exception(e)
            log.error("更新/插入错误")
            self.session.rollback()

    # --------------------------  Cell  --------------------------

    def get_all_cell_info(
        self, excel: str = None, sheet: str = None
    ) -> list[CellInfoPO]:
        """列出数据库所有 Cell"""
        stmt = select(CellInfoPO, ExcelSheetPO).join(
            ExcelSheetPO, ExcelSheetPO.id == CellInfoPO.exsh_id
        )
        if excel:
            stmt = stmt.where(ExcelSheetPO.excel == excel)
        if sheet:
            stmt = stmt.where(ExcelSheetPO.sheet == sheet)

        return self.session.scalars(stmt).all()

    def upsert_cell(self, po: CellInfoPO) -> int:
        try:
            # 查询 exsh
            old_po = self.cell_repo.get_cell_by_uk(po)
            # 更新
            if old_po:
                po.id = old_po.id
                new_po = self.exsh_repo.update_by_id(po)
            # 新增
            else:
                new_po = self.cell_repo.insert_one(po)
            self.session.commit()
            return new_po.id
        except Exception:
            # log.exception(e)
            log.error("更新/插入 Cell 错误")
            self.session.rollback()

    # --------------------------  Trans  --------------------------

    def get_not_translated_cells(
        self, bo: ExcelSheetBO, src: str, dst: str, col: int
    ) -> list[CellInfoPO]:
        """获得【所有】【未翻译过】的 Cell"""
        stmt = build_sql_get_all_not_translated_cells(bo, src, dst, col)
        res = self.session.scalars(stmt).all()
        # 执行 SQL
        return res

    def get_all_not_processed_cells(
        self, bo: ExcelSheetBO, src: str, col: int = None
    ) -> list[ExcelSheetPO, CellInfoPO]:
        """获得【所有】【翻译过】但是【没有预处理】 的 Cell
        为什么返回两个对象：处理 Ref 可能需要 excel 和 sheet 信息
        """
        stmt = build_sql_get_not_proc_cells(bo, src, col)
        # 执行 SQL
        res = self.session.execute(stmt).all()
        return res

    def get_all_not_processed_trans(
        self, bo: ExcelSheetBO, src: str, dst: str, col: str
    ) -> list[ExcelSheetPO, CellInfoPO, TransInfoPO]:
        """获得【所有】【没有处理过】的【翻译】(ExcelSheetPO, CellInfoPO, TransInfoPO)
        为什么要返回三个对象：处理引用需要 excel 和 sheet 的信息
        """
        stmt = build_sql_get_all_not_proc_trans(bo, src, dst, col)
        res = self.session.execute(stmt).all()
        return res

    def get_all_write_trans(
        self, bo: ExcelSheetBO, src: str, dst: str, col: int
    ) -> list[CellInfoPO, TransInfoPO]:
        """获取该 exsh 下所有的已经翻译过的结果"""
        stmt = build_sql_get_all_write_trans(bo, src, dst, col)
        res = self.session.execute(stmt).all()
        return res

    def get_all_trans_info(self):
        """数据库列出所有 trans_info 信息"""
        return self.trans_repo.list_all()

    def upsert_trans_info(self, po: TransInfoPO) -> int:
        """数据库列出 trans_info 信息"""
        try:
            # 查询 cell
            old_po = self.trans_repo.get_trans_by_uk(po)
            if old_po:
                po.id = old_po.id
                new_po = self.trans_repo.update_by_id(po)
            else:
                new_po = self.trans_repo.insert_one(po)
            self.session.commit()
            return new_po.id
        except Exception:
            log.error("增加 trans info 错误")
            # log.exception(e)
            self.session.rollback()
