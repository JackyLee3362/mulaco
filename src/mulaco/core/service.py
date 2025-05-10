import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from mulaco.core.db_models import Base, CellInfo, ExcelSheet, TransInfo
from mulaco.core.repo import CellInfoRepo, ExcelSheetRepo, TransInfoRepo

log = logging.getLogger(__name__)


class DbService:
    """数据库服务"""

    def __init__(self, db_url: str) -> None:
        """连接 + 设置数据库"""
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.setup_repo()

    def setup_repo(self) -> None:
        """初识设置"""
        self.exsh_repo = ExcelSheetRepo(self.session)
        self.cell_repo = CellInfoRepo(self.session)
        self.trans_repo = TransInfoRepo(self.session)

    def get_exsh_by_name(self, excel_name: str, sheet_name: str) -> ExcelSheet:
        """根据 excel 名字 + sheet 名字获得 exsh 对象(记录)"""
        return self.exsh_repo.get_by_exsh_name(excel_name, sheet_name)

    def get_all_exsh(self) -> list[ExcelSheet]:
        """获得所有数据库中的 exsh 对象(记录)"""
        return self.exsh_repo.list_all()

    # TODO 待优化
    # TODO 待测试
    def delete_exsh(self, exsh: ExcelSheet) -> None:
        """软删除数据库中的 exsh 对象(记录)"""
        try:
            # 删除所有 excels
            exsh.delete = True
            self.exsh_repo.update_by_exsh_name(exsh)

            # 删除所有 cells
            self.cell_repo.batch_delete_by_exid(exsh.id)
            cells = self.cell_repo.get_list_by_cond((CellInfo.exsh_id == exsh.id))

            # 删除所有 trans
            for cell in cells:
                self.trans_repo.batch_delete_by_cell_id(cell.id)

            self.session.commit()
        except Exception:
            log.error("删除 excel sheet 错误")
            self.session.rollback()

    def upsert_exsh(self, exsh: ExcelSheet):
        """数据库新增/更新 exsh"""
        try:
            exsh = self.exsh_repo.update_by_exsh_name(exsh)
            self.session.commit()
            return exsh
        except Exception:
            log.error("增加 excel sheet 错误")
            self.session.rollback()

    def get_all_cell_info(self):
        """数据库列出所有 cell"""
        return self.cell_repo.list_all()

    def add_cell_info(self, excel: str, sheet: str, cell: CellInfo):
        """数据库新增 cell 数据"""
        try:
            exsh = self.exsh_repo.get_by_exsh_name(excel, sheet)
            cell.exsh_id = exsh.id
            self.cell_repo.update_by_cell_info(cell)
            self.session.commit()
        except Exception as e:
            log.exception(e)
            log.error("增加 cell info 错误")
            self.session.rollback()

    def get_all_translated_cell(
        self, src: str, dst: str, excel: str, sheet: str, col: int
    ):
        """获得所有已经翻译过的 Cell"""
        stmt = (
            select(ExcelSheet, CellInfo, TransInfo)
            .where(
                ExcelSheet.excel == excel,
                ExcelSheet.sheet == sheet,
                CellInfo.src_lang == src,
                CellInfo.col == col,
                TransInfo.dst_lang == dst,
                ExcelSheet.delete.is_(False),
                CellInfo.delete.is_(False),
                TransInfo.delete.is_(False),
            )
            .join(CellInfo, ExcelSheet.id == CellInfo.exsh_id)
            .join(TransInfo, CellInfo.id == TransInfo.cell_id)
        )
        return self.session.execute(stmt)

    def get_all_trans_info(self):
        """数据库列出所有 trans_info 信息"""
        return self.trans_repo.list_all()

    def add_trans_info(self, exsh: ExcelSheet, cell: CellInfo, trans: TransInfo):
        """数据库列出 trans_info 信息"""
        try:
            exsh = self.exsh_repo.get_by_exsh_name(exsh.excel, exsh.sheet)
            cell.exsh_id = exsh.id
            cell = self.cell_repo.get_by_cell_info(cell)
            trans.cell_id = cell.id
            self.trans_repo.update_by_trans_info(trans)
        except Exception:
            log.error("增加 trans info 错误")
            self.session.rollback()
