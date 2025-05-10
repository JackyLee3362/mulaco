from __future__ import annotations

import json
import os
import re
from abc import ABCMeta, abstractmethod
from functools import cached_property, lru_cache
from logging import getLogger
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
from mulaco.core.service import DbService as DbService

log = getLogger(__name__)


class TranslateApi(metaclass=ABCMeta):
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


class ServiceCache:

    CACHE_TBL = "default-service-cache"
    GLOSSARY_KEY = "glossary-key"

    def __init__(self, cache: JsonCache):
        self.cache = cache

    def get_gid_key(self, src: str, dst: str):
        return f"{src}-{dst}"

    def cache_get_gid(self, src: str, dst: str) -> str:
        key = self.get_gid_key(src, dst)
        if not isinstance(key, str):
            raise TypeError("Glossary key 必须是 str")
        d: dict = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        return d.get(src)

    def cache_set_gid(self, src: str, dst: str, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Glossary value 必须是 str")
        key = self.get_gid_key(src, dst)
        d: dict = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        d[key] = value
        self.cache.set(self.GLOSSARY_KEY, d, self.CACHE_TBL)

    def cache_del_gid(self, src: str, dst: str):
        gid_key = self.get_gid_key(src, dst)
        d: dict = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        val = d.pop(gid_key, None)
        self.cache.set(self.GLOSSARY_KEY, d, self.CACHE_TBL)
        return val


class LocalApi(TranslateApi, ServiceCache):
    """本地缓存翻译，主要加载本地的术语字典"""

    CACHE_TBL = "local-trans-cache"

    def __init__(self, cache: JsonCache):
        self.cache = cache
        ServiceCache.__init__(self, cache)

    def api_translate_text(self, src: str, dst: str, text: str):
        self.cache_get_gid(src, dst)

    def load_dict_glossary(self, d: dict[str, dict[str, dict[str, str]]]):
        """根据字段创建术语表
        字典类似于
        {
            "en-zh":{"hello":"你好","world":"世界"}
        }
        """
        for src, d1 in d.items():
            for dst, d2 in d1.items():
                self.api_create_glossary(src, dst, d2)

    def _create_or_update_glossary(self, src: str, dst: str, entries: str):
        tbl = self.CACHE_TBL
        gid = "gid-" + self.get_gid_key(src, dst)
        d: dict = self.cache.get(gid, tbl, {})
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
        """在本地的 Cache 创建术语表

        Args:
            src (str): 原语言
            dst (str): 目标语言
            entries (dict): 翻译的对照表
        """
        key = self.get_gid_key(src, dst)
        cached_glossary_id = self.cache_get_gid(src, dst)
        if cached_glossary_id:
            log.warning(f"cache 中已经存在 {key} 值，无法再新建，请先删除该键")
            return
        gid = self._create_or_update_glossary(src, dst, entries)
        self.cache_set_gid(src, dst, gid)
        return gid

    def api_get_glossary(self, src: str, dst: str):
        """获取本地术语表"""
        gid = self.cache_get_gid(src, dst)
        return self.cache.get(gid, self.CACHE_TBL, {})

    def api_delete_glossary(self, src: str, dst: str):
        """删除本地术语表"""
        # 删除缓存
        gid = self.cache_del_gid(src, dst)
        # 删除客户端数据
        if gid:
            self._delete_glossary(gid)

    def api_list_glossaries(self):
        """罗列本地术语表"""
        return self.cache.get(self.GLOSSARY_KEY, tbl=self.CACHE_TBL, default=[])


class DeepLApi(TranslateApi, ServiceCache):
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
        ServiceCache.__init__(self, cache)

    def api_translate_text(self, src: str, dst: str, text: str):
        """翻译文字"""
        glossary_id = self.cache_get_gid(src, dst)
        res = self.cli.translate_text(
            text=text, source_lang=src, target_lang=dst, glossary=glossary_id
        )
        return res.text

    def api_create_glossary(self, src: str, dst: str, entries: dict):
        """
        // 在某个 tbl 中
        "1":{
            "key":"glossary_key",
            "value": { // 其实就是 d
                "en-zh":"abcdefghijklmn",
                "en-jp":"abcdefg1234567",
            }
        }

        """
        # 校验: 缓存中存在键不可以创建
        key = self.get_gid_key(src, dst)
        cached_glossary_id = self.cache_get_gid(src, dst)
        if cached_glossary_id:
            log.warning(f"cache 中已经存在 {key} 值，无法再新建，请先删除该键")
            return
        glossary = self.cli.create_glossary(
            name=key, source_lang=src, target_lang=dst, entries=entries
        )
        id = glossary.glossary_id
        self.cache_set_gid(src, dst, id)
        return id

    def api_delete_glossary(self, src: str, dst: str):
        key = self.get_gid_key(src, dst)
        log.warning(f"delete_glossary: {key}")
        # 删除缓存
        id = self.cache_del_gid(src, dst)
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
                self.cache_set_gid(src, dst, item.glossary_id)
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


class TencentApi(TranslateApi):
    """DeepLApi 客户端"""

    name = "tencent-cloud"

    CACHE_TBL = "tencent-cache"

    def __init__(self, cache: JsonCache):
        self.cache = cache
        id = os.getenv("TENCENTCLOUD_SECRET_ID")
        key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        cred = credential.Credential(id, key)
        self.client = tmt_client.TmtClient(cred, "ap-shanghai")

    def api_translate_text(self, src, dst, text):
        req = models.TextTranslateRequest()
        req.Source = src
        req.SourceText = text
        req.Target = dst
        req.ProjectId = 0
        resp = self.client.TextTranslate(req)
        return resp.TargetText

    def api_create_glossary(self, src, dst, entries):
        return super().api_create_glossary(src, dst, entries)

    def api_get_glossary(self, src, dst):
        return super().api_get_glossary(src, dst)

    def api_list_glossaries(self):
        return super().api_list_glossaries()

    def api_delete_glossary(self, src, dst):
        return super().api_delete_glossary(src, dst)
