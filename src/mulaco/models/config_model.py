from __future__ import annotations

import time

# 语言业务模型
# 因为是配置文件导入的，所以是 VO
from dataclasses import dataclass, field
from pathlib import Path

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class LanguageVO:
    name: str
    code: str
    active: bool = field(default=True)
    offset: int = field(default=None)
    service_name: str = field(default=None)
    service: object = field(init=False, repr=False)


@dataclass_json
@dataclass
class LanguagesVO:
    langs: list[LanguageVO]


@dataclass_json
@dataclass
class SheetVO:
    sheet_name: str
    lang_cols: dict[str, list[str]]
    header_row: int = field(repr=False)
    max_row: int = field(repr=False, default=None)
    max_col: int = field(repr=False, default=None)  # index 从 1 开始
    is_term: bool = field(default=False, repr=False)


# ref_excel: Optional[str] = field(default=None)
# ref_sheet: Optional[str] = field(default=None)
# params: Optional[dict] = field(default=None)


@dataclass_json
@dataclass
class ExcelVO:
    excel_name: str
    sheets: list[SheetVO]
    skip: bool = field(default=False, repr=False)
    src_path: str = field(default=None, repr=False)
    dst_path: str = field(default=None, repr=False)

    def from_dict(self, *args, **kwargs) -> ExcelVO: ...

    def to_dict(self, *args, **kwargs) -> dict: ...


@dataclass_json
@dataclass
class BatchExcelVO:
    src_dir: str
    dst_dir: str
    excels: list[ExcelVO]

    # 控制缓存是否更新
    modify_time: int = field(default_factory=time.time)

    def __post_init__(self):
        src = Path(self.src_dir)
        dst = Path(self.dst_dir)
        for excel in self.excels:
            excel.src_path = str(src.joinpath(excel.excel_name))
            excel.dst_path = str(dst.joinpath(excel.excel_name))

    def from_dict(self, *args, **kwargs) -> BatchExcelVO: ...

    def to_dict(self, *args, **kwargs) -> BatchExcelVO: ...
