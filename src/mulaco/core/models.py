from dataclasses import dataclass, field


@dataclass
class ExcelSheetBO:
    excel: str
    sheet: str
    header: int = field(default=None)


@dataclass
class CellInfoBO:
    row: int
    col: int
    src_lang: str
    raw_text: str = field(default=None)
    exsh: ExcelSheetBO = field(default=None)
    proc_text: str = field(default=None)


@dataclass
class TransInfoBO:
    dst_lang: str
    cell: CellInfoBO = field(default=None)
    trans_text: str = field(default=None)
    write_text: str = field(default=None)
