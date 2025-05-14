import logging
from typing import Optional

from mulaco.base.cache import JsonCache
from mulaco.core.app import App
from mulaco.db.repo import T

log = logging.getLogger(__name__)


class LocalGidCache:
    """主要类似于
    CACHE_TBL 表中
    "key": "glossary-key",
    "val": {
        "en-zh": "gid-en-zh" # 这是本地的 gid
        "en-jp": "abcedfghij" # 这是 deepL 的 gid
    }
    """

    CACHE_TBL = "default-gid-cache"
    GLOSSARY_KEY = "glossary-key"

    def __init__(self, cache: JsonCache):
        self.cache = cache

    def get_gid_key(self, src: str, dst: str):
        return f"{src}-{dst}"

    def get_all_gid(self):
        return self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})

    def get_cached_gid(self, src: str, dst: str) -> Optional[str]:
        """获取 gid，如果没有则为空"""
        gid_key = self.get_gid_key(src, dst)
        # 获取 gid 字典
        d: dict = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        return d.get(gid_key)

    def set_cached_gid(self, src: str, dst: str, gid: str) -> None:
        """设置 gid"""
        if not isinstance(gid, str):
            raise TypeError("Glossary value 必须是 str")
        gid_key = self.get_gid_key(src, dst)
        # 获取 gid 字典
        d: dict = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        d[gid_key] = gid
        self.cache.set(self.GLOSSARY_KEY, d, self.CACHE_TBL)
        return gid

    def del_cached_gid(self, src: str, dst: str):
        """删除 gid"""
        gid_key = self.get_gid_key(src, dst)
        # 获取 gid 字典
        d: dict = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        val = d.pop(gid_key, None)
        self.cache.set(self.GLOSSARY_KEY, d, self.CACHE_TBL)
        return val


class LocalDictCache:
    """本地缓存翻译，主要加载本地的术语字典"""

    name = "local-cli"
    CACHE_TBL = "local-cli-cache"

    def __init__(self, app: App):
        # 用户自定义字典
        self.user_dict = app.user_dict
        # 缓存的 key
        self.user_ordered_key: dict[str, list] = {}
        self._init_dict()

    def _init_dict(self):
        for src, d1 in self.user_dict.items():
            for dst, d2 in d1.items():
                s = sorted(d2.keys(), key=lambda x: -len(x))
                self.user_ordered_key.setdefault(src, {})
                self.user_ordered_key[dst] = s
        log.info("本地用户字典排序成功")

    def api_translate_text(self, src: str, dst: str, text: str):
        d = self.user_dict.get(src, {}).get(dst, {})
        sorted_key = self.user_ordered_key.get(src, {}).get(dst, [])
        # 单词替换(从长词替换)
        # TODO FEATURE 未实现 替换时不替换标签内的内容
        translated_text = text
        # TODO 优化 遍历比较费时，是否有更好的算法（生成正则表达式？）
        for key in sorted_key:
            if key in translated_text:
                # TODO 单词的复数形式，小写形式等
                translated_text = translated_text.replace(key, d[key])
        return translated_text
        return translated_text
