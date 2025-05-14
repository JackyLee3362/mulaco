from __future__ import annotations

import logging
import re
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from dataclasses_json import dataclass_json

from mulaco.excel.utils import excel_col_num2alpha
from mulaco.models.dto_model import ExcelDTO

log = logging.getLogger(__name__)


@dataclass_json
@dataclass
class RefMeta:
    excel: int
    sheet: str
    col: str
    row: str

    def __post_init__(self):
        self.excel = int(self.excel)

    def to_tag(self, idx: int):
        return f'<ref id="{idx}" />'

    def to_ref(self, dir: str, ex_name: str, ref_col: int = 0):
        col = excel_col_num2alpha(ref_col)
        res = rf'''"&'{dir}/[{ex_name}]{self.sheet}'!${col}${self.row}&"'''
        res = rf'''"&'[{self.excel}]{self.sheet}'!${col}${self.row}&"'''
        return res

    def from_dict(self, d: dict) -> RefMeta: ...

    def to_dict(self) -> dict: ...


class FixRePattern:
    # 英文模式
    RE_EN = re.compile(r"[a-zA-Z][a-zA-Z\.\s\-]+")
    # 括号模式
    RE_BRACKET = re.compile(r"\(.*\)")
    # 数字模式
    RE_NUMBER = re.compile(r"\d+")
    # 中文模式
    RE_CN = re.compile(r"[\u4e00-\u9fa5]+")
    # excel 计算模式
    RE_CALCULATE = re.compile(r'^="(.*)"$')
    # 引用模式
    REF_PATTERN = re.compile(r'"&\[(.+?)\](.+?)\!\$([A-Z]+?)\$(\d+?)&"')
    # tag 模式
    TAG_PATTERN = re.compile(r"""<("[^"]*"|'[^']*'|[^'">])*>""")
    # 特殊 tag 模式
    RE_TAG_COLOR = re.compile(r"<color=#[a-zA-Z0-9]{6}>|<\/color>|<sprite=\d+>|\{0\}")
    # ROOT tag
    RE_ROOT_TAG = re.compile(r"^<root>(.*)<\/root>$")
    # 自替换 REF
    SELF_REF_PATTERN = re.compile(r'(?<="&)(\[\d+\])(?=.+?\!\$[A-Z]+\$\d+&")')
    # "&\[(\d+)\](?=.+?\!\$[A-Z]+?\$\d+?)&"


parser_res = namedtuple("ParserResult", ["res", "msg"])


class CellParser:
    TAG_ROOT = "root"
    TAG_REF = "ref"
    parser = "html.parser"
    has_cal_key = "has_cal"
    refs_key = "refs"

    def self_fix_ref(self, path: str, ex_name, text: str) -> bool:
        _, msg = self.text_ref_to_tag(text)
        if msg:
            # 说明有 ref
            txt = FixRePattern.SELF_REF_PATTERN.sub(f"{path}/[{ex_name}]", text)
            log.debug(f"修复: {text} -> {txt}")
            return txt
        return text

    def pre_parser(self, text: str) -> tuple[str, dict]:
        info = {}
        text, msg = self.text_del_cal(text)
        if msg:
            info[self.has_cal_key] = True
        text, msg = self.text_ref_to_tag(text)
        if msg:
            # 如果有肯定是 dict
            info[self.refs_key] = [m.to_dict() for m in msg]
        if len(info):
            return text, info
        else:
            return text, None

    def post_parser(
        self,
        text: str,
        info: dict,
        ref_dtos: list[ExcelDTO] = [],
        order: int = None,
        total: int = None,
    ) -> str:
        if info is None:
            return text
        if info.get(self.refs_key):
            text = self.text_add_root_tag(text)
            refs = [RefMeta.from_dict(d) for d in info.get(self.refs_key)]
            # 计算 ref_abs_cols 类似 [14, 18] 这样的绝对值
            ref_info = self.calculate_ref_abs_cols(refs, ref_dtos, order, total)

            text = self.text_tag_to_ref(text, refs, ref_info)
            text = self.text_del_root_tag(text)
        if info.get(self.has_cal_key):
            text = self.text_add_cal(text)
        return text

    def text_add_root_tag(self, text: str) -> str:
        return f"<{self.TAG_ROOT}>{text}</{self.TAG_ROOT}>"

    def text_del_root_tag(self, text: str):
        return FixRePattern.RE_ROOT_TAG.sub(r"\1", text)

    def text_add_cal(self, text: str) -> str:
        return f'="{text}"'

    def text_del_cal(self, text: str) -> parser_res:
        if FixRePattern.RE_CALCULATE.match(text):
            new_text = FixRePattern.RE_CALCULATE.sub(r"\1", text)
            return parser_res(new_text, True)
        return parser_res(text, False)

    def text_ref_to_tag(self, text: str) -> parser_res:
        refs = []
        idx = 0

        def ref_substr(match: re.Match):
            nonlocal idx
            ref_info = RefMeta(*[g for g in match.groups()])
            refs.append(ref_info)
            r = ref_info.to_tag(idx)
            idx += 1
            return r

        new_text = FixRePattern.REF_PATTERN.sub(ref_substr, text)
        if len(refs):
            return parser_res(new_text, refs)
        return parser_res(new_text, None)

    # 该函数逻辑较为复杂
    def calculate_ref_abs_cols(
        self, refs: list[RefMeta], ref_dtos: list[ExcelDTO], order: int, total: int
    ) -> list[tuple[str, str, int]]:
        res = []
        # 遍历 ref_meta
        for ref_meta in refs:
            idx = ref_meta.excel
            # 找到对应的 dto
            dto = ref_dtos[idx - 1]
            # 找到对应的 sheet
            for sheet in dto.sheets:
                if sheet.sheet_name == ref_meta.sheet:
                    # 找到对应的 cols
                    cols = sheet.lang_cols[sheet.use_src_lang]
                    # 计算 col 在其中的位置
                    factor = cols.index(ref_meta.col)
                    # 取出 max_col
                    max_col = sheet.max_col
                    ref_col = max_col + factor * total + order
                    ref_dir = str(Path(dto.dst_path).parent.absolute())
                    # 将反斜杠替换为正斜杠
                    ref_dir = ref_dir.replace("\\", "/")
                    res.append((ref_dir, dto.excel_name, ref_col))
        return res

    def text_tag_to_ref(
        self, text: str, refs: list[RefMeta], ref_info: list[tuple[str, str, int]]
    ) -> str:
        """ref_info 是 (引用excel的绝对路径, excel名, 引用列绝对值) 的列表"""
        soup = BeautifulSoup(text, self.parser)
        for ele in soup.find_all(self.TAG_REF):
            id = int(ele.get("id"))
            ref = refs[id]
            ref_dir, ref_excel, ref_col = ref_info[id]
            s = ref.to_ref(ref_dir, ref_excel, ref_col)
            ele.replace_with(s)
        new_text = str(soup)
        # & 符号会被转义，所以要手动替换
        new_text = new_text.replace("&amp;", "&")
        return new_text
