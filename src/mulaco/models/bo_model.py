#  业务模型


from dataclasses import dataclass, field


@dataclass
class ExcelSheetBO:
    id: int = field(default=None)
    excel: str = field(default=None)
    sheet: str = field(default=None)
    header: int = field(default=None)


@dataclass
class CellInfoBO:
    row: int = field(default=None)
    col: int = field(default=None)
    src_lang: str = field(default=None)
    id: int = field(default=None)
    exsh_id: int = field(default=None)
    raw_text: str = field(default=None)
    proc_text: str = field(default=None)


@dataclass
class TransInfoBO:
    id: int = field(default=None)
    dst_lang: str = field(default=None)
    cell_id: int = field(default=None)
    trans_text: str = field(default=None)
    write_text: str = field(default=None)
