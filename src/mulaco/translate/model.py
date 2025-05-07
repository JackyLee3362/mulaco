from functools import lru_cache


class Language:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code

    def __str__(self):
        return self.code


class Languages:
    zh = Language("简中", "zh")
    en = Language("英语", "en")
    jp = Language("日语", "ja")

    de = Language("德语", "de")
    ko = Language("韩语", "ko")
    th = Language("泰语", "th")
    ru = Language("俄语", "ru")
    es = Language("西语", "es")
    fr = Language("法语", "fr")
    pt = Language("葡语", "pt-br")
    it = Language("意语", "it")

    deepl = [de, ko, ru, es, fr, pt, it]
    tencent = [th]
    src_langs: list[Language] = [en, zh]
    dst_langs: list[Language] = [de, ko, th, ru, es, fr, pt, it]
    fixed_lang = set([ko, th, ru])


@lru_cache
def get_lang_by_code(code: str) -> Language:
    for dst_lang in Languages.dst_langs:
        if dst_lang.code == code:
            return dst_lang
