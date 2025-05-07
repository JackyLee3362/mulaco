import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mulaco.core.db_models import Base, CellInfo, ExcelSheet, TransInfo
from mulaco.core.repo import CellInfoRepo, ExcelSheetRepo, TransInfoRepo

log = logging.getLogger(__name__)


class DbService:
    """数据库服务"""

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.setup_repo()

    def setup_repo(self):
        self.exsh_repo = ExcelSheetRepo(self.session)
        self.cell_repo = CellInfoRepo(self.session)
        self.trans_repo = TransInfoRepo(self.session)

    def get_all_exsh(self):
        return self.exsh_repo.list()

    def add_exsh(self, exsh: ExcelSheet):
        try:
            self.exsh_repo.update_by_exsh_name(exsh)
            self.session.commit()
        except Exception:
            log.error("增加 excel sheet 错误")
            self.session.rollback()

    def get_all_cell_info(self):
        return self.cell_repo.list()

    def add_cell_info(self, exsh: ExcelSheet, cell: CellInfo):
        try:
            exsh = self.exsh_repo.get_by_exsh_name(exsh)
            cell.exsh_id = exsh.id
            self.cell_repo.update_by_cell_info(cell)
        except Exception:
            log.error("增加 cell info 错误")
            self.session.rollback()

    def get_all_trans_info(self):
        return self.trans_repo.list()

    def add_trans_info(self, exsh: ExcelSheet, cell: CellInfo, trans: TransInfo):
        try:
            exsh = self.exsh_repo.get_by_exsh_name(exsh)
            cell.exsh_id = exsh.id
            cell = self.cell_repo.get_by_cell_info(cell)
            trans.cell_id = cell.id
            self.trans_repo.update_by_trans_info(trans)
        except Exception:
            log.error("增加 trans info 错误")
            self.session.rollback()
