import re
from dataclasses import dataclass

from bs4 import BeautifulSoup

from mulaco.excel.utils import excel_col_alpha_increment


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

    def to_ref(self, offset: int = 0):
        col = excel_col_alpha_increment(self.col, offset)
        res = f'"&[{self.excel}]{self.sheet}!${col}${self.row}&"'
        return res


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


class CellParser:
    TAG_ROOT = "root"
    TAG_REF = "ref"
    parser = "html.parser"

    def text_add_root_tag(self, text: str):
        return f"<{self.TAG_ROOT}>{text}</{self.TAG_ROOT}>"

    def text_del_root_tag(self, text: str):
        return FixRePattern.RE_ROOT_TAG.sub(r"\1", text)

    def excel_add_cal(self, text: str):
        return f'="{text}"'

    def excel_del_cal(self, text: str):
        return FixRePattern.RE_CALCULATE.sub(r"\1", text)

    def excel_ref_to_tag(self, text: str) -> tuple[str, list[RefMeta]]:
        refs = []
        idx = 0

        def ref_substr(match: re.Match):
            ref_info = RefMeta(*[g for g in match.groups()])
            refs.append(ref_info)
            return ref_info.to_tag(idx)

        new_text = FixRePattern.REF_PATTERN.sub(ref_substr, text)
        return new_text, refs

    def excel_tag_2_ref(self, text: str, offset: int, refs: list[RefMeta]) -> str:
        soup = BeautifulSoup(text, self.parser)
        for ele in soup.find_all(self.TAG_REF):
            id = int(ele.get("id"))
            ref = refs[id]
            s = ref.to_ref(offset)
            ele.replace_with(s)
        new_text = str(soup)
        # & 符号会被转义，所以要手动替换
        new_text = new_text.replace("&amp;", "&")
        return new_text
