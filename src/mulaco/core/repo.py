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

    def list_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取对象列表（支持分页）"""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def get_list_by_cond(self, condi: List) -> List[T]:
        stmt = select(self.model).where(*condi)
        return self.session.scalars(stmt).all()

    def insert_one(self, instance: T) -> T:
        self.session.add(instance)
        return instance

    def insert_all(self, instances: List[T]) -> None:
        self.session.add_all(instances)

    def update_by_id(self, instance: T) -> T:
        new_instance = self.session.merge(instance)
        return new_instance


class ExcelSheetRepo(BaseRepo[ExcelSheet]):
    """表信息 Repo"""

    def __init__(self, session):
        super().__init__(ExcelSheet, session)

    def get_by_exsh_name(self, excel_name: str, sheet_name: str) -> ExcelSheet:
        return self.session.scalar(
            select(ExcelSheet).where(
                ExcelSheet.excel == excel_name, ExcelSheet.sheet == sheet_name
            )
        )

    def update_by_exsh_name(self, exsh: ExcelSheet) -> ExcelSheet:
        obj = self.get_by_exsh_name(exsh.excel, exsh.sheet)
        if obj:
            exsh.id = obj.id
        return self.update_by_id(exsh)


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

    def update_by_cell_info(self, cell: CellInfo) -> CellInfo:
        obj = self.get_by_cell_info(cell)
        if obj:
            cell.id = obj.id
        return self.update_by_id(cell)

    def batch_delete_by_exid(self, exid: int) -> None:
        objs = self.get_list_by_cond((CellInfo.exsh_id == exid))
        for obj in objs:
            obj.delete = True
            self.session.merge(obj)


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

    def update_by_trans_info(self, info: TransInfo) -> TransInfo:
        obj = self.get_by_trans_info(info)
        if obj:
            info.id = info.id
        return self.update_by_id(info)

    def batch_delete_by_cell_id(self, cell_id: int) -> None:
        objs = self.get_list_by_cond((TransInfo.cell_id == cell_id))
        for obj in objs:
            obj.delete = True
            self.session.merge(obj)
