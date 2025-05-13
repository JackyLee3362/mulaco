import pytest

from mulaco.fix.parser import CellParser, FixRePattern, RefMeta


@pytest.fixture(scope="module")
def parser():
    parser = CellParser()
    return parser


text_1 = '="During battles, ally Yaolings: "&[1]Main!$N$4&"."'
text_2 = 'During battles, ally Yaolings: "&[1]Main!$N$4&".'
text_3 = 'During battles, ally Yaolings: <ref id="0" />.'
# (翻译)
text_4 = '<root>During battles, ally Yaolings: <ref id="0" />.</root>'
text_5 = 'During battles, ally Yaolings: <ref id="0" />.'
text_6 = 'During battles, ally Yaolings: "&[1]Main!$N$4&".'
text_7 = '="During battles, ally Yaolings: "&[1]Main!$N$4&"."'


def test_1_del_cal(parser: CellParser):
    res = parser.excel_del_cal(text_1)
    assert res == text_2
    # print(res)


def test_2_ref_to_tag(parser: CellParser):
    res = parser.excel_ref_to_tag(text_2)
    assert res[0] == text_3
    # print(res)


def test_3_add_root_tag(parser: CellParser):
    res = parser.text_add_root_tag(text_3)
    assert res == text_4
    # print(res)


def test_del_root_tag(parser: CellParser):
    res = parser.text_del_root_tag(text_4)
    assert res == text_5
    # print(res)


def test_tag_2_ref(parser: CellParser):
    res = parser.excel_tag_2_ref(text_5, 0, [RefMeta(1, "Main", "N", "4")])
    assert res == text_6
    # print(res)


def test_add_cal(parser: CellParser):
    res = parser.excel_add_cal(text_6)
    assert res == text_7
    # print(res)
