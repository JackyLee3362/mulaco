import logging
from typing import Generic, List, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from mulaco.models.db_model import CellInfoPO, ExcelSheetPO, TransInfoPO

log = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepo(Generic[T]):
    """基础Repository类
    设计原则: Repo 层不处理事务
    """

    def __init__(self, model: type[T], session: Session):
        self.model = model
        self.session = session

    def list_all(self, skip: int = 0, limit: int = 0) -> List[T]:
        """获取对象列表（支持分页）"""
        stmt = select(self.model).offset(skip)
        if limit > 0:
            stmt.limit(limit)
        return list(self.session.scalars(stmt).all())

    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def get_one_by_condi(self, condi: tuple) -> T:
        stmt = select(self.model).where(*condi)
        return self.session.scalar(stmt)

    def get_list_by_cond(self, condi: tuple) -> List[T]:
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


class ExcelSheetRepo(BaseRepo[ExcelSheetPO]):
    """表信息 Repo"""

    def __init__(self, session):
        super().__init__(ExcelSheetPO, session)

    def get_exsh_by_uk(self, excel: str, sheet: str) -> ExcelSheetPO:
        return self.get_one_by_condi(
            (ExcelSheetPO.excel == excel, ExcelSheetPO.sheet == sheet)
        )


class CellInfoRepo(BaseRepo[CellInfoPO]):
    """单元格信息 Repo"""

    def __init__(self, session):
        super().__init__(CellInfoPO, session)

    def get_cell_by_uk(self, po: CellInfoPO) -> CellInfoPO:
        return self.get_one_by_condi(
            (
                CellInfoPO.exsh_id == po.exsh_id,
                CellInfoPO.row == po.row,
                CellInfoPO.col == po.col,
            )
        )

    def batch_delete_by_exid(self, exid: int) -> None:
        old_objs = self.get_list_by_cond((CellInfoPO.exsh_id == exid))
        for obj in old_objs:
            obj.is_delete = True
            self.session.merge(obj)


class TransInfoRepo(BaseRepo[TransInfoPO]):
    """翻译信息 Repo"""

    def __init__(self, session):
        super().__init__(TransInfoPO, session)

    def get_trans_by_uk(self, po: TransInfoPO) -> TransInfoPO:
        return self.get_one_by_condi(
            (TransInfoPO.cell_id == po.cell_id, TransInfoPO.dst_lang == po.dst_lang)
        )

    def batch_delete_by_cell_id(self, cell_id: int) -> None:
        objs = self.get_list_by_cond((TransInfoPO.cell_id == cell_id))
        for obj in objs:
            obj.is_delete = True
            self.session.merge(obj)
