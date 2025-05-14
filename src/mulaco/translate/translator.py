from __future__ import annotations

import os
from abc import ABCMeta, abstractmethod
from logging import getLogger

# 腾讯服务需要
from time import sleep
from typing import Optional

# pip install deepl
import deepl

# pip install --upgrade tencentcloud-sdk-python-common
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)

# pip install --upgrade tencentcloud-sdk-python-tmt
from tencentcloud.tmt.v20180321 import models, tmt_client

from mulaco.core.app import App
from mulaco.db.db import DbService as DbService
from mulaco.translate.helper import LocalDictCache, LocalGidCache

log = getLogger(__name__)


class Translator(metaclass=ABCMeta):
    name = "api-name"

    @abstractmethod
    def api_translate_text(self, src: str, dst: str, text: str) -> str: ...


class DeepLTranslator(Translator, LocalGidCache):
    """DeepLApi 客户端"""

    name = "deepl-pro"

    DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")
    CACHE_TBL = "deepl-cache"

    def __init__(self, app: App):
        # 初始化 Gid 缓存
        LocalGidCache.__init__(self, app.cache)
        self.cache = app.cache
        # 用户字典
        self.user_dict = app.user_dict
        self.cli: deepl.Translator = None
        self.init_cli()

    def init_cli(self):
        log.info("初始化 DeepL 客户端")
        if self.DEEPL_AUTH_KEY is None:
            log.warning("DeepL 未配置密钥，请在环境变量中设置 DEEPL_AUTH_KEY")
            return
        try:
            self.cli = deepl.Translator(self.DEEPL_AUTH_KEY)
            self.init_glossoaries()

        except Exception:
            log.warning("初始化 DeepL 客户端错误，请联系开发人员")

    def init_glossoaries(self):
        log.debug("deepL 使用用户字典初始化远程术语库")
        # 如果没有但是
        res: list[deepl.GlossaryInfo] = self.cli.list_glossaries()
        _d = self.get_all_gid()
        if len(res) != len(_d):
            log.warning("删除所有远程术语库")
            # 说明存在冗余，删除所有远程 glossary
            for r in res:
                self.cli.delete_glossary(r.glossary_id)

        for src, d1 in self.user_dict.items():
            for dst, d2 in d1.items():
                self._sync_glossary(src, dst, d2)

    def api_translate_text(self, src: str, dst: str, text: str):
        """翻译文字"""
        glossary_id = self.get_cached_gid(src, dst)
        res = self.cli.translate_text(
            text=text, source_lang=src, target_lang=dst, glossary=glossary_id
        )
        return res.text

    def _sync_glossary(self, src: str, dst: str, entries: dict):
        """远程同步/创建 glossary"""
        # 缓存中存在键不可以创建
        key = self.get_gid_key(src, dst)
        cached_glossary_id = self.get_cached_gid(src, dst)
        src_dst_dict = self.user_dict.get(src, {}).get(dst, {})
        if cached_glossary_id:
            res = self._get_glossary(src, dst)
            if len(src_dst_dict) == res.entry_count:
                log.debug(f"存在 {key} 值，且 deepL 术语库条目与本地字典相同，无需更新")
                return
            else:
                # 远程存在，但是条目数量不一样，删除
                self.del_cached_gid(cached_glossary_id)
                log.debug(f"存在 {key} 值，且 deepL 术语库条目与本地字典不同，删除远程")
        glossary = self.cli.create_glossary(
            name=key, source_lang=src, target_lang=dst, entries=entries
        )
        id = glossary.glossary_id
        self.set_cached_gid(src, dst, id)
        log.debug(f"deepL 创建术语库 key = {id}")
        return id

    def _get_glossary(self, src: str, dst: str) -> Optional[deepl.GlossaryInfo]:
        key = self.get_gid_key(src, dst)
        d = self.cache.get(self.GLOSSARY_KEY, self.CACHE_TBL, {})
        glossary_id = d.get(key)
        if glossary_id:
            return self.cli.get_glossary(glossary_id)


class TencentTranslator(Translator):
    """DeepLApi 客户端"""

    name = "tencent-cloud"
    TENCENTCLOUD_SECRET_ID = os.getenv("TENCENTCLOUD_SECRET_ID")
    TENCENTCLOUD_SECRET_KEY = os.getenv("TENCENTCLOUD_SECRET_KEY")
    REGION = "ap-shanghai"

    CACHE_TBL = "tencent-cache"

    def __init__(self, app: App):
        self.client: tmt_client.TmtClient = None
        self.local_cli = LocalDictCache(app)
        self.init_cli()

    def init_cli(self):
        log.info("初始化 腾讯云翻译 客户端")
        id = self.TENCENTCLOUD_SECRET_ID
        key = self.TENCENTCLOUD_SECRET_KEY
        if None in (id, key):
            log.warning("未配置腾讯云翻译 API")
            return
        cred = credential.Credential(id, key)
        self.client = tmt_client.TmtClient(cred, self.REGION)

    def api_translate_text(self, src, dst, text):
        local_trans = self.local_cli.api_translate_text(src, dst, text)
        try:
            req = models.TextTranslateRequest()
            req.Source = src
            req.SourceText = local_trans
            req.Target = dst
            req.ProjectId = 0
            resp = self.client.TextTranslate(req)
            sleep(0.2)
            return resp.TargetText
        except TencentCloudSDKException as e:
            log.error(e)


class MockTranslator(Translator):
    name = "mock-cli"
    CACHE_TBL = "mock-cache"

    def __init__(self, app: App):
        self.cache = app.cache
        self.local_cli = LocalDictCache(app)
        log.info("初始化本地 Mock 客户端")

    def api_translate_text(self, src, dst, text):
        text = self.local_cli.api_translate_text(src, dst, text)
        res = f"{src}-{dst}({text})"
        return res
