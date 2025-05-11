from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

# dataclasses-json
from dataclasses_json import dataclass_json


# @dataclass_json
@dataclass
class SheetDTO:
    sheet_name: str
    lang_cols: dict[str, list[str]]
    header_row: int = field(repr=False)
    max_row: int = field(init=False, repr=False, default=0)
    max_col: int = field(init=False, repr=False, default=0)  # index 从 1 开始
    is_term: bool = field(default=False, repr=False)

    # ref_excel: Optional[str] = field(default=None)
    # ref_sheet: Optional[str] = field(default=None)
    # params: Optional[dict] = field(default=None)


@dataclass_json
@dataclass
class ExcelDTO:
    excel_name: str
    sheets: list[SheetDTO]
    skip: bool = field(default=False, repr=False)
    src_path: str = field(init=False, repr=False)
    dst_path: str = field(init=False, repr=False)

    def from_dict(self, *args, **kwargs) -> ExcelDTO: ...

    def to_dict(self, *args, **kwargs) -> ExcelDTO: ...


@dataclass_json
@dataclass
class BatchExcel:
    src_dir: str
    dst_dir: str
    excels: list[ExcelDTO]

    # 控制缓存是否更新
    modify_time: int = field(default_factory=time.time)

    def __post_init__(self):
        src = Path(self.src_dir)
        dst = Path(self.dst_dir)
        for excel in self.excels:
            excel.src_path = str(src.joinpath(excel.excel_name))
            excel.dst_path = str(dst.joinpath(excel.excel_name))

    def from_dict(self, *args, **kwargs) -> BatchExcel: ...

    def to_dict(self, *args, **kwargs) -> BatchExcel: ...
