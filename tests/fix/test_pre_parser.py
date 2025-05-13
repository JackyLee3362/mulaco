import pytest

from mulaco.fix.parser import CellParser


@pytest.fixture(scope="module")
def parser():
    parser = CellParser()
    return parser


def test_1_正常文本(parser: CellParser):
    text_1 = "hello, world"
    res = parser.pre_parser(text_1)
    print(res)


def test_2_正常文本_带计算(parser: CellParser):
    text_1 = '="hello, world"'
    res = parser.pre_parser(text_1)
    print(res)


def test_2_引用文本(parser: CellParser):
    text_1 = '="During battles, ally Yaolings: "&[1]Main!$N$4&"."'
    res = parser.pre_parser(text_1)
    print(res)
