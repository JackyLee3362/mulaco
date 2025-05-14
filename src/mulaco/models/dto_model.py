from __future__ import annotations

import time

# 语言业务模型
# 可以看作是配置服务向下传递的 DTO
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class LanguageDTO:
    name: str
    code: str
    active: bool = field(default=True)
    order: Optional[int] = field(default=None)
    service_name: Optional[str] = field(default=None)
    service: Optional[object] = field(repr=False, default=None)

    def from_dict(self, *args, **kwargs) -> LanguageDTO: ...

    def to_dict(self, *args, **kwargs) -> dict: ...


@dataclass_json
@dataclass
class LanguagesConfigDTO:
    langs: dict[str, LanguageDTO]
    dst_langs: list[str] = field(init=None, default_factory=list)

    def __post_init__(self):
        dst_langs = []
        for lang_str, lang_obj in self.langs.items():
            if lang_obj.active:
                dst_langs.append(lang_str)
        self.dst_langs = sorted(dst_langs, key=lambda x: self.langs[x].order)

    def from_dict(self, *args, **kwargs) -> LanguagesConfigDTO: ...

    def to_dict(self, *args, **kwargs) -> dict: ...


@dataclass_json
@dataclass
class SheetDTO:
    sheet_name: str
    lang_cols: dict[str, list[str]]
    header_row: int = field(repr=False)
    use_src_lang: str = field(repr=False)
    max_row: Optional[int] = field(repr=False, default=None)
    max_col: Optional[int] = field(repr=False, default=None)  # index 从 1 开始
    is_term: bool = field(default=False, repr=False)

    def from_dict(self, *args, **kwargs) -> SheetDTO: ...

    def to_dict(self, *args, **kwargs) -> dict: ...


@dataclass_json
@dataclass
class ExcelDTO:
    excel_name: str
    sheets: list[SheetDTO]
    skip: bool = field(default=False, repr=False)
    src_path: Optional[str] = field(default=None, repr=False)
    dst_path: Optional[str] = field(default=None, repr=False)
    refs: list[str] = field(default_factory=list, repr=False)

    def from_dict(self, *args, **kwargs) -> ExcelDTO: ...

    def to_dict(self, *args, **kwargs) -> dict: ...


@dataclass_json
@dataclass
class BatchExcelDTO:
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
        # 删除 skip 文件
        excels = []
        for excel in self.excels:
            if not excel.skip:
                excels.append(excel)
        self.excels = excels

    def from_dict(self, *args, **kwargs) -> BatchExcelDTO: ...

    def to_dict(self, *args, **kwargs) -> dict: ...
