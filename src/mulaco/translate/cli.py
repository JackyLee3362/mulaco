from __future__ import annotations

import os
from abc import ABCMeta, abstractmethod
from logging import getLogger

# 腾讯服务需要
from time import sleep

# pip install deepl
import deepl

# pip install --upgrade tencentcloud-sdk-python-common
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)

# pip install --upgrade tencentcloud-sdk-python-tmt
from tencentcloud.tmt.v20180321 import models, tmt_client

from mulaco.base.db import JsonCache
from mulaco.core.app import App
from mulaco.db.service import DbService as DbService

log = getLogger(__name__)


class TranslateCli(metaclass=ABCMeta):
    name = "api-name"

    @abstractmethod
    def api_translate_text(self, src: str, dst: str, text: str) -> str: ...

    @abstractmethod
    def api_create_glossary(self, src: str, dst: str, entries: dict) -> str: ...

    @abstractmethod
    def api_get_glossary(self, src: str, dst: str) -> dict: ...

    @abstractmethod
    def api_delete_glossary(self, src: str, dst: str) -> None: ...

    @abstractmethod
    def api_list_glossaries(self) -> dict: ...


class GidCache:
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

    def get_cached_gid(self, src: str, dst: str) -> str | None:
        """获取 gid，如果没有则为空"""
        gid_key = self.get_gid_key(src, dst)
        if not isinstance(gid_key, str):
            raise TypeError("Glossary key 必须是 str")
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


class LocalCli(TranslateCli, GidCache):
    """本地缓存翻译，主要加载本地的术语字典"""

    CACHE_TBL = "local-cli-cache"

    def __init__(self, app: App):
        GidCache.__init__(self, app.cache)
        self.app = app
        self.cache = app.cache
        # 将用户自定义的字典放入术语表中
        self.load_dict_glossary(app.user_dict)

    def api_translate_text(self, src: str, dst: str, text: str):
        d = self.api_get_glossary(src, dst)
        # 单词替换(从小词替换)
        sorted_key = sorted(d.keys(), key=len)
        translated_text = text
        for key in sorted_key:
            translated_text = translated_text.replace(key, d[key])
        return translated_text

    def load_dict_glossary(self, d: dict[str, dict[str, dict[str, str]]]):
        for src, d1 in d.items():
            for dst, entries in d1.items():
                self.api_create_glossary(src, dst, entries)

    def generate_gid(self, src: str, dst: str):
        return f"gid-{src}-{dst}"

    def update_glossary(self, src: str, dst: str, entries: str):
        """根据字段创建/更新术语表
        字典类似于
        "key": "gid-en-zh",
        "val": {
            "hello":"你好",
            "world":"世界"
        }
        """
        tbl = self.CACHE_TBL
        gid = self.get_cached_gid(src, dst)
        # 如果 gid-cache 不存在该 gid
        d: dict = self.cache.get(gid, tbl, {})
        # 更新术语表
        d.update(entries)
        self.cache.set(gid, d, tbl)
        return gid

    def _delete_glossary(self, gid: str):
        tbl = self.CACHE_TBL
        d: dict = self.cache.get(gid, tbl, {})
        d.pop(gid, None)
        self.cache.set(gid, d, tbl)
        return gid

    def api_create_glossary(self, src: str, dst: str, entries: dict):
        """在本地的 Cache 创建/更新术语表

        Args:
            src (str): 原语言
            dst (str): 目标语言
            entries (dict): 翻译的对照表
        """
        gid = self.get_cached_gid(src, dst)
        if gid is None:
            # 创建 gid
            gid = self.generate_gid(src, dst)
            gid = self.set_cached_gid(src, dst, gid)
        # 然后更新数据
        gid = self.update_glossary(src, dst, entries)
        return gid

    def api_get_glossary(self, src: str, dst: str):
        """获取本地术语表"""
        gid = self.get_cached_gid(src, dst)
        return self.cache.get(gid, self.CACHE_TBL, {})

    def api_delete_glossary(self, src: str, dst: str):
        """删除本地术语表"""
        # 删除缓存
        gid = self.del_cached_gid(src, dst)
        # 删除客户端数据
        if gid:
            self._delete_glossary(gid)

    def api_list_glossaries(self):
        """罗列本地术语表"""
        return self.cache.get(self.GLOSSARY_KEY, tbl=self.CACHE_TBL, default=[])


class DeepLCli(TranslateCli, GidCache):
    """DeepLApi 客户端"""

    name = "deepl-pro"

    DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")
    CACHE_TBL = "deepl-cache"

    def __init__(self, cache: JsonCache):
        """初始化

        Args:
            db (DbService): 存翻译结果的
            cache (KVCache): 存 glossary id 的
        """
        self.cache = cache
        self.cli = deepl.Translator(self.DEEPL_AUTH_KEY)
        GidCache.__init__(self, cache)

    def api_translate_text(self, src: str, dst: str, text: str):
        """翻译文字"""
        glossary_id = self.get_cached_gid(src, dst)
        res = self.cli.translate_text(
            text=text, source_lang=src, target_lang=dst, glossary=glossary_id
        )
        return res.text

    def api_create_glossary(self, src: str, dst: str, entries: dict):
        """
        在 CACHE_TBL 表中，其类似于
        "key":"glossary_key",
        "val": {
            "en-zh":"abcdefghijklmn",
            "en-jp":"abcdefg1234567",
        }
        """
        # 校验: 缓存中存在键不可以创建
        key = self.get_gid_key(src, dst)
        cached_glossary_id = self.get_cached_gid(src, dst)
        if cached_glossary_id:
            # TODO 可以删除该 glossary 然后更新
            log.warning(f"cache 中已经存在 {key} 值，无法再新建，请先删除该键")
            return
        glossary = self.cli.create_glossary(
            name=key, source_lang=src, target_lang=dst, entries=entries
        )
        id = glossary.glossary_id
        self.set_cached_gid(src, dst, id)
        return id

    def api_delete_glossary(self, src: str, dst: str):
        key = self.get_gid_key(src, dst)
        log.warning(f"delete_glossary: {key}")
        # 删除缓存
        id = self.del_cached_gid(src, dst)
        if id:
            # 删除 glossary
            self.cli.delete_glossary(id)

    def api_list_glossaries(self, sync=False):
        """列出 glossaries

        Args:
            sync (bool, optional): 同步 Cache 中的值
        """
        res = self.cli.list_glossaries()
        if sync:
            for item in res:
                src = item.source_lang.lower()
                dst = item.target_lang.lower()
                self.set_cached_gid(src, dst, item.glossary_id)
        return res

    def api_get_glossary(self, src: str, dst: str):
        key = self.get_gid_key(src, dst)
        d = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        glossary_id = d.get(key)
        if glossary_id:
            res = self.cli.get_glossary(glossary_id)
            log.debug(f"从 DeepL 获取 glossary id: {glossary_id}")
            return res
        else:
            log.warning(f"Cache 中不存在 glossary key: {key}")


class TencentCli(TranslateCli):
    """DeepLApi 客户端"""

    name = "tencent-cloud"

    CACHE_TBL = "tencent-cache"

    def __init__(self, app: App):
        self.cache = app.cache
        id = os.getenv("TENCENTCLOUD_SECRET_ID")
        key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        cred = credential.Credential(id, key)
        self.client = tmt_client.TmtClient(cred, "ap-shanghai")
        self.local_cli = LocalCli(app)

    def api_translate_text(self, src, dst, text):
        try:
            req = models.TextTranslateRequest()
            req.Source = src
            req.SourceText = text
            req.Target = dst
            req.ProjectId = 0
            resp = self.client.TextTranslate(req)
        except TencentCloudSDKException as e:
            log.error(e)
        return resp.TargetText

    def api_create_glossary(self, src, dst, entries):
        return self.local_cli.api_create_glossary(src, dst, entries)

    def api_get_glossary(self, src, dst):
        return self.local_cli.api_get_glossary(src, dst)

    def api_list_glossaries(self):
        return self.local_cli.api_list_glossaries()

    def api_delete_glossary(self, src, dst):
        return self.local_cli.api_delete_glossary(src, dst)


class MockCli(TranslateCli):
    name = "mock-cli"
    CACHE_TBL = "mock-cache"

    def __init__(self, app: App):
        self.cache = app.cache
        self.local_cli = LocalCli(app)
        super().__init__()

    def api_translate_text(self, src, dst, text):
        text = self.local_cli.api_translate_text(src, dst, text)
        res = f"{src}-{dst}({text})"
        return res

    def api_create_glossary(self, src, dst, entries):
        return self.local_cli.api_create_glossary(src, dst, entries)

    def api_get_glossary(self, src, dst):
        return self.local_cli.api_get_glossary(src, dst)

    def api_list_glossaries(self):
        return self.local_cli.api_list_glossaries()

    def api_delete_glossary(self, src, dst):
        return self.local_cli.api_delete_glossary(src, dst)
