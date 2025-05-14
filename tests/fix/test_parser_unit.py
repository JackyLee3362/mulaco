import pytest

from mulaco.fix.parser import CellParser, FixRePattern, RefMeta


@pytest.fixture(scope="module")
def parser():
    parser = CellParser()
    return parser


text_1 = '="During battles, ally Yaolings: "&[1]Main!$N$4&"."'
# 去掉 cal
text_2 = 'During battles, ally Yaolings: "&[1]Main!$N$4&".'
# ref 正则替换为 tag
text_3 = 'During battles, ally Yaolings: <ref id="0" />.'
# (翻译)
text_4 = 'During battles, ally Yaolings: <ref id="0" />.'
# 新增 root
text_5 = '<root>During battles, ally Yaolings: <ref id="0" />.</root>'
# ref-tag 替换为 ref
text_6 = "<root>During battles, ally Yaolings: \"&'[1]Main'!$L$4&\".</root>"
# 删除 root
text_7 = "During battles, ally Yaolings: \"&'[1]Main'!$L$4&\"."
# 新增 cal
text_8 = '="During battles, ally Yaolings: "&\'[1]Main\'!$L$4&"."'


def test_1_del_cal(parser: CellParser):
    res = parser.text_del_cal(text_1)
    assert res.res == text_2
    # print(res)


def test_2_ref_to_tag(parser: CellParser):
    res = parser.text_ref_to_tag(text_2)
    assert res.res == text_3
    # print(res)


# ----- 翻译 -----


def test_3_add_root_tag(parser: CellParser):
    res = parser.text_add_root_tag(text_4)
    assert res == text_5
    # print(res)


def test_tag_2_ref(parser: CellParser):

    res = parser.text_tag_to_ref(
        text_5,
        [RefMeta(1, "Main", "N", "4")],
        [("path/to/excel/", "Foo.xlsx", 12)],
    )
    assert res == text_6
    # print(res)


def test_del_root_tag(parser: CellParser):
    res = parser.text_del_root_tag(text_6)
    assert res == text_7
    # print(res)


def test_add_cal(parser: CellParser):
    res = parser.text_add_cal(text_7)
    assert res == text_8
    # print(res)
