import pytest

from mulaco.fix.parser import CellParser, RefMeta


@pytest.fixture(scope="module")
def parser():
    parser = CellParser()
    return parser


def test_1_正常文本(parser: CellParser):
    text_1 = "hello, world"
    res = parser.post_parser(text_1, None)
    print(res)


def test_2_正常文本_带计算(parser: CellParser):
    text_1 = "hello, world"
    res = parser.post_parser(text_1, {"has_cal": True})
    print(res)


def test_2_引用文本(app, parser: CellParser):
    text_1 = 'During battles, ally Yaolings: <ref id="0" />.'
    excel_dtos = app.batch_excels.excels
    excel_dto = excel_dtos[0]
    sheet = excel_dto.sheets[0]
    sheet.max_col = 100
    col = sheet.lang_cols["en"][0]

    res = parser.post_parser(
        text_1,
        {"has_cal": True, "refs": [RefMeta(1, sheet.sheet_name, col, "4").to_dict()]},
        ref_dtos=excel_dtos,
        order=1,
        total=8,
    )
    print(res)
