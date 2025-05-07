from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class ExcelSheet(Base):
    """定义数据位置"""

    __tablename__ = "excel_sheet"
    # 需要 id 去关联
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="工作表 ID"
    )
    excel: Mapped[str] = mapped_column(String(length=255), comment="工作薄名称")
    sheet: Mapped[str] = mapped_column(String(length=255), comment="表名称")
    header: Mapped[int] = mapped_column(comment="标题起始行", default=1)

    # 唯一索引约束
    __table_args__ = (UniqueConstraint("excel", "sheet", name="uk_excel_sheet"),)

    def __repr__(self) -> str:
        return f"<ExcelSheet(id={self.id}, excel={self.excel}, sheet={self.sheet}, header={self.header})>"

    def __str__(self) -> str:
        return f"ExcelSheet({self.excel}.{self.sheet})"


class CellInfo(Base):
    """定义Excel原始表数据"""

    __tablename__ = "cell_info"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exsh_id: Mapped[int] = mapped_column(comment="Excel Sheet Id")
    # 用数字方便排序
    row: Mapped[int] = mapped_column(comment="使用行")
    col: Mapped[int] = mapped_column(comment="使用列")
    # 原始语言，包括 zh, en, ru 等
    src_lang: Mapped[str] = mapped_column(String(length=16), comment="原始语言")
    src_text: Mapped[str] = mapped_column(
        String(length=2048), comment="原始文本", default=""
    )
    # 处理过的文本(processed text)，带标签和引用的
    proc_text: Mapped[str] = mapped_column(
        String(length=2048), comment="处理过的文本", nullable=True
    )

    # 自定义类型，用于扩展，一般来说
    # - 0x00 普通类型
    # - 0x01 带标签的文本，需要使用 proc_text
    # - 0x10 带引用的文本，需要使用 proc_text
    # - 0x11 带标签和引用的文本，需要使用 proc_text
    type: Mapped[int] = mapped_column(default=0)

    # 唯一索引约束
    __table_args__ = (
        UniqueConstraint("exsh_id", "row", "col", name="uk_exsh_row_col"),
    )

    def __repr__(self) -> str:
        return f"<CellInfo(id={self.id}, exid={self.exsh_id}, loc({self.row}, {self.col}), lang={self.src_lang}, text={self.src_text})>"

    def __str__(self) -> str:
        return f"CellInfo(loc({self.row}, {self.col}), lang={self.src_lang}, text={self.src_text})"


class TransInfo(Base):
    """翻译后的信息"""

    __tablename__ = "trans_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cell_id: Mapped[int] = mapped_column(comment="CellInfo中对应的 id")
    dst_lang: Mapped[int] = mapped_column(comment="目标语言")
    trans_text: Mapped[str] = mapped_column(comment="直翻后的文本", default="")
    dst_text: Mapped[str] = mapped_column(comment="处理后的文本", nullable=True)

    __table_args__ = (UniqueConstraint("cell_id", "dst_lang", name="uk_cell_lang"),)

    def __repr__(self) -> str:
        return f"<TransInfo(id={self.id}, cell_id={self.cell_id}, dst_lang={self.dst_lang}, trans_text={self.trans_text})>"

    def __str__(self) -> str:
        return f"TransInfo(dst_lang={self.dst_lang}, dst_text={self.dst_text})"
