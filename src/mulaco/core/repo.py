import logging
from typing import Generic, List, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from mulaco.core.db_models import CellInfo, ExcelSheet, TransInfo

log = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepo(Generic[T]):
    """基础Repository类
    设计原则: Repo 层不处理事务
    """

    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session

    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取对象列表（支持分页）"""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def insert_one(self, instance: T) -> T:
        self.session.add(instance)
        return instance

    def insert_all(self, instances: List[T]) -> None:
        self.session.add_all(instances)

    def update_by_id(self, instance: T) -> T:
        self.session.merge(instance)


class ExcelSheetRepo(BaseRepo[ExcelSheet]):
    """表信息 Repo"""

    def __init__(self, session):
        super().__init__(ExcelSheet, session)

    def get_by_exsh_name(self, exsh: ExcelSheet) -> ExcelSheet:
        return self.session.scalar(
            select(ExcelSheet).where(
                ExcelSheet.excel == exsh.excel, ExcelSheet.sheet == exsh.sheet
            )
        )

    def update_by_exsh_name(self, exsh: ExcelSheet) -> None:
        obj = self.get_by_exsh_name(exsh)
        if obj:
            exsh.id = obj.id
        self.update_by_id(exsh)


class CellInfoRepo(BaseRepo[CellInfo]):
    """单元格信息 Repo"""

    def __init__(self, session):
        super().__init__(CellInfo, session)

    def get_by_cell_info(self, cell: CellInfo) -> CellInfo:
        return self.session.scalar(
            select(CellInfo).where(
                CellInfo.exsh_id == cell.exsh_id,
                CellInfo.row == cell.row,
                CellInfo.col == cell.col,
            )
        )

    def update_by_cell_info(self, cell: CellInfo) -> None:
        obj = self.get_by_cell_info(cell)
        if obj:
            cell.id = obj.id
        self.update_by_id(cell)


class TransInfoRepo(BaseRepo[TransInfo]):
    """翻译信息 Repo"""

    def __init__(self, session):
        super().__init__(TransInfo, session)

    def get_by_trans_info(self, info: TransInfo) -> TransInfo:
        return self.session.scalar(
            select(TransInfo).where(
                TransInfo.cell_id == info.cell_id, TransInfo.dst_lang == info.dst_lang
            )
        )

    def update_by_trans_info(self, info: TransInfo) -> None:
        obj = self.get_by_trans_info(info)
        if obj:
            info.id = info.id
        self.update_by_id(info)
