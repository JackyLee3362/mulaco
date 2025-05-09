import json
from io import StringIO
from pprint import pprint


def test_1():
    d = {"en": {"zh": {"hello": "你好", "world": "世界"}}}
    s = json.dumps(d)
    f = StringIO(s)
    d2 = json.load(f)
    pprint(d2)


def test_2():
    d = {"en": {"zh": {"hello": "你好", "world": "世界"}}}
    src_lang = "en"
    dst_lang = "zh"
    text = "hello"
    res = d.get(src_lang, {}).get(dst_lang, {}).get(text, text)
    assert res == "你好"
    text = "good"
    res = d.get(src_lang, {}).get(dst_lang, {}).get(text, text)
    assert res == "good"
