from __future__ import annotations

import json
import os
import re
from abc import ABCMeta, abstractmethod
from functools import cached_property, lru_cache
from logging import getLogger
from time import sleep

import deepl
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.tmt.v20180321 import models, tmt_client

from mulaco.base import AppBase
from mulaco.core.service import DbService as DbService

from .db import TransInfoTable
from .model import Language, Languages

log = getLogger(__name__)


class TranslateService:
    def __init__(self, db: DbService, app_db: AppBase):
        self.db = db
        self.app_db = app_db
        self.services: dict[Language, TranslateApi] = {}
        self.json_dict: dict = {}
        self.en_pattern = re.compile(r"[a-zA-Z][a-zA-Z\.\s\-]+")
        self.bracket_pattern = re.compile(r"\(.*\)")
        self.number_pattern = re.compile(r"\d+")
        self.tag_pattern = re.compile(
            r"<color=#[a-zA-Z0-9]{6}>|<\/color>|<sprite=\d+>|\{0\}"
        )
        self.cn_pattern = re.compile(r"[\u4e00-\u9fa5]+")
        # self.level_pattern = re.compile(r"[\s\-]?(III|II|IV|VIII|VII|VI|V|I|SP|NPC)")
        self.level_pattern = re.compile(r"[A-Z]+")

        self.json_file = "E:/Project/mulaco/json/batch2.json"
        self.load_json_repl()

    @cached_property
    def api_tencent_service(self):
        return self.services.get(Languages.th)

    @cached_property
    def api_deepl_service(self):
        return self.services.get(Languages.de)

    def load_json_repl(self):
        try:
            self.json_dict = json.load(open(self.json_file, "r", encoding="utf-8"))
        except Exception:
            self.json_dict = {}

    def save_json_file(self):
        json.dump(
            self.json_dict,
            open(self.json_file, "w", encoding="utf-8"),
            ensure_ascii=False,
        )

    def register(
        self,
        langs: list[Language],
        service: TranslateApi,
    ):
        for lang in langs:
            self.services[lang] = service

    def translate(self):
        en = Languages.en
        for dst_lang, service in self.services.items():
            key = f"{en}_{dst_lang}"
            res = self.db.get_not_translate(en.code, dst_lang.code)
            total = len(res)

            log.debug(f"{key}: 剩余未翻译的数量 {total}")
            for idx, item in enumerate(res, 1):
                if item.dst_text:
                    log.debug(f"{key}:[{idx}/{total}] 已经翻译过，跳过")
                    continue
                dst_text = self._translate(en.code, dst_lang.code, service, item)
                log.debug(
                    f"({en}/{dst_lang})[{idx}/{total}]: {item.src_text} -> {dst_text}"
                )
                item.dst_text = dst_text
                if idx % 10 == 0:
                    log.info("提交到数据库")
                    self.db.session.commit()
            self.db.session.commit()

    def _translate(
        self, src_lang: str, dst_lang: str, service: TranslateApi, item: TransInfoTable
    ):
        text = item.src_text
        params_key = f"{item.excel_name}/{item.sheet_name}/params"
        params: dict = eval(self.db.get_or_default(params_key, "{}")) or {}
        en_col = params.get("split_col", None)
        flag = False
        if en_col is not None:
            if src_lang == "en":
                flag = en_col == item.col
            if src_lang == "zh":
                zh_cols_key = f"{item.excel_name}/{item.sheet_name}/zh_cols"
                en_cols_key = f"{item.excel_name}/{item.sheet_name}/en_cols"
                zh_cols = eval(self.db.get_or_default(zh_cols_key, "[]")) or []
                en_cols = eval(self.db.get_or_default(en_cols_key, "[]")) or []
                flag = en_cols.index(en_col) == zh_cols.index(item.col)
        if flag and "," in text:  # 如果需要 split 则 split
            splited = text.split(",")
            if len(splited) != 2:  # 如果 split 后长度不是 2 则不 split
                log.warning(f"翻译参数错误 {text}")
                return text
            t1 = splited[0]
            t2 = splited[1]
            dst_1, dst_2 = "", ""
            if t1 is not None and t1 != "":
                dst_1 = service.api_translate_text(src_lang, dst_lang, t1)
            if t2 is not None and t2 != "":
                dst_2 = service.api_translate_text(src_lang, dst_lang, t2)
            dst_text = f"{dst_1},{dst_2}"
        else:
            dst_text = service.api_translate_text(src_lang, dst_lang, text)
        return dst_text

    def fix_tag(self):
        for dst_lang, service in self.services.items():
            # 只管泰语，韩文和俄语
            res = (
                self.db.query_by_condition(
                    src_lang=Languages.en.code,
                    dst_lang=dst_lang.code,
                    excel="CharmConfig.xlsx",
                    col="I",
                )
                .filter(TransInfoTable.src_text.isnot(None))
                .all()
            )
            log.debug(f"{dst_lang}: 总计为 {len(res)}")
            key = f"{Languages.en.code}-{dst_lang}-tag"
            for item in res:
                parts = self.tag_pattern.split(item.src_text)
                d = self.json_dict.get(key, {})
                for part in parts:
                    if part == "" or part == " ":
                        continue
                    if part in d:
                        log.debug(f"{key}: {part}")
                    else:
                        _trans = service.api_translate_text(
                            Languages.en.code, dst_lang.code, part
                        )
                        d[part] = _trans
                        self.json_dict[key] = d
                        self.save_json_file()
                dst_text = item.src_text
                test_text_list = []
                for part in parts:
                    if part == "" or part == " ":
                        continue
                    dst_text = dst_text.replace(part, d[part])
                    test_text_list.append(d[part])
                test_test = "".join(test_text_list)
                if (
                    not self.is_good_trans(item.src_text, test_test)
                    and dst_lang in Languages.fixed_lang
                ):
                    log.warning(f"{key}: {item.src_text} -> {dst_text}")
                    pass

                log.info(f"{key}: {item.src_text} -> {dst_text}")
                item.dst_text = dst_text
                item.write_text = dst_text
            self.db.session.commit()

    def special_fix(self):
        res = (
            self.db.query_by_condition(
                src_lang="en", dst_lang="ko", excel="NpcConfig.xlsx"
            )
            .filter(TransInfoTable.dst_text.isnot(None))
            .all()
        )

        cnt = 0
        for item in res:
            zh_item = self.get_zh_item(item)
            # if self.special_filter(item.src_text, item.write_text):
            if not self.special_is_good(item.src_text, item.write_text):
                cnt += 1
                log.info(f"{item.src_text} -> {zh_item.write_text}")
                trans_res = self.do_manual_trans(en_item=item, zh_item=zh_item)
                if trans_res is not None:
                    item.dst_text = trans_res
                    item.write_text = trans_res
                    zh_item.dst_text = trans_res
                    item.zh_col = None
                self.db.session.commit()

        log.info(f"需要修复的数量为 {cnt}/{len(res)}")

    def special_filter(self, src_text, dst_text):
        src_text = src_text or ""
        dst_text = dst_text or ""
        dst_str = ["look", "find", "demon"]
        for s in dst_str:
            if s in src_text.lower() and "." not in src_text:
                return True
        return False

    def special_is_good(self, src_text, dst_text):
        src_text = src_text or ""
        dst_text = dst_text or ""
        if len(dst_text) >= 4:
            return False
        special_symbol = [",", ".", " "]
        for sym in special_symbol:
            in_src = sym in src_text
            in_dst = sym in dst_text
            if in_src != in_dst:
                return False
        return True

    def fix_translate(self):
        self.special_fix()
        return
        en = Languages.en
        zh = Languages.zh
        for dst_lang, service in self.services.items():
            # 只管泰语，韩文和俄语
            if dst_lang not in Languages.fixed_lang:
                continue
            res = (
                self.db.query_by_condition(
                    src_lang=en.code,
                    dst_lang=dst_lang.code,
                )
                .filter(TransInfoTable.dst_text.isnot(None))
                .all()
            )

            total = len(res)
            for idx, en_item in enumerate(res, 1):
                if self.is_good_trans(en_item.src_text, en_item.dst_text, False):
                    log.debug(f"en: {dst_lang} 翻译结果正确，跳过")
                    continue
                log.debug("翻译有问题")
                # 说明需要使用中文翻译修复
                # 如果存在对应的中文翻译
                # :todo: 本来数据库应该存储相对应的数据
                zh_item = self.get_zh_item(en_item)
                # if zh_item.write_text:
                #     pass
                # logger.debug(f"zh: {dst_lang} 中文翻译结果正确，跳过")
                # continue
                zh_src_text = zh_item.src_text
                zh_dst_text = zh_item.dst_text
                zh_ = zh.code
                dst_ = dst_lang.code
                if zh_dst_text is None:
                    mark = input("是否需要翻译(yes/no)")
                    if mark.lower().startswith("y") or mark == "":
                        zh_dst_text = self._translate(zh_, dst_, service, zh_item)
                        zh_item.dst_text = zh_dst_text
                log.debug(
                    f"{zh}/{dst_lang})[{idx}/{total}]: 翻译后 {zh_src_text} -> {zh_dst_text}"
                )
                # 首先对 dst_text 进行关键词替换
                repl_text = self.do_text_replace(
                    zh_dst_text, zh_item.src_lang, zh_item.dst_lang
                )
                # 保存到模型中
                zh_item.dst_text = repl_text

                # 判断 dst_text 是否修复成功
                _trans_good = self.is_good_trans(zh_src_text, zh_dst_text)
                if _trans_good:
                    zh_item.write_text = repl_text
                else:
                    manual_trans = self.do_manual_trans(en_item, zh_item)
                    zh_item.dst_text = manual_trans
                    zh_item.write_text = manual_trans
                self.db.session.commit()

    def is_good_trans(self, src_text: str, dst_text: str, is_zh=True):
        bracket = self.bracket_pattern
        flag = True
        dst_text = self.level_pattern.sub("", dst_text)
        if self.cn_pattern.search(dst_text):
            return False

        if self.tag_pattern.search(dst_text):
            # todo: 暂时不考虑 tag_pattern
            return flag
        if self.en_pattern.search(dst_text):
            log.warning("修复存在问题：存在英文")
            flag = False
        # 对于 en_lang 只检查英文
        if not is_zh:
            return flag

        if ";" not in src_text and ";" in dst_text:
            log.warning("修复存在问题：存在分号;")
            flag = False

        if bracket.search(dst_text):
            log.warning("修复存在问题：存在括号()")
            flag = False

        # if "," in src_text and "," not in dst_text:
        #     logger.warning("修复存在问题：src 存在逗号, 但 dst 没有逗号")
        #     flag = False

        if not self.number_pattern.search(src_text) and self.number_pattern.search(
            dst_text
        ):
            log.warning("修复存在问题：存在数字")
            flag = False
        return flag

    def delete_db_glossary(self) -> None:
        for src_lang in Languages.src_langs:
            for dst_lang, service in self.services.items():
                key = f"{src_lang}_{dst_lang}"
                # 从数据库中查找
                res = self.app_db.get_or_default(key)
                log.debug(f"{key}:{res}")
                if res:
                    service.api_delete_glossary(res.value)
                    self.app_db.set(key, "")

    def create_glossary(self) -> str:
        for src_lang in Languages.src_langs:
            for dst_lang, service in self.services.items():
                key = f"{src_lang}_{dst_lang}"
                glossary_id = self.app_db.get_or_default(key)
                if glossary_id:
                    log.debug(f"{key} 已经创建过，跳过")
                    continue
                entry_objs = self.db.get_all_terms(src_lang.code, dst_lang.code)
                entries = {e.origin_text: e.dst_text for e in entry_objs}

                log.debug(f"{key} 准备创建 {entries}")
                value = service.api_create_glossary(
                    key, src_lang.code, dst_lang.code, entries
                )
                self.app_db.set(key, value)

    def get_zh_item(self, en_item: TransInfoTable) -> TransInfoTable:
        _excel = en_item.excel_name
        _sheet = en_item.sheet_name
        _col = en_item.col
        zh = Languages.zh.code
        dst_lang = en_item.dst_lang
        _zh_col = en_item.zh_col
        if _zh_col is None:
            en_key = f"{_excel}/{_sheet}/en_cols"
            raw_en_val = self.db.get_or_default(en_key, "[]")
            en_val: list[str] = eval(raw_en_val)
            zh = Languages.zh.code
            dst_lang = en_item.dst_lang
            if _col in en_val:
                en_col_idx = en_val.index(_col)
            else:
                log.warning("数据不存在")
                return None
            zh_key = f"{_excel}/{_sheet}/zh_cols"
            raw_zh_val = self.db.get_or_default(zh_key, "[]")
            zh_val: list[str] = eval(raw_zh_val)
            _zh_col = zh_val[en_col_idx]
        zh_col = _zh_col

        zh_query = self.db.query_by_condition(
            excel=en_item.excel_name,
            sheet=en_item.sheet_name,
            src_lang=zh,
            dst_lang=dst_lang,
            col=zh_col,
            row=en_item.row,
            is_term=en_item.is_term,
        )
        zh_item = zh_query.first()
        en_item.zh_col = zh_col
        return zh_item

    def do_text_replace(self, text: str, src_lang: str, dst_lang: str):
        key = f"{src_lang}-{dst_lang}"
        d: dict = self.json_dict.get(key, {})
        for item in self.en_pattern.findall(text):
            if item in d:
                v = d[item]
                text = text.replace(item, v)
                log.debug(f"替换 {item} -> {v}")
        return text

    def do_manual_trans(self, en_item: TransInfoTable, zh_item: TransInfoTable):
        key = f"{zh_item.src_lang}-{zh_item.dst_lang}-src"
        d: dict = self.json_dict[key]
        _src_text = zh_item.src_text
        _json_dst_text = d.get(_src_text, None)

        if _json_dst_text:
            log.debug(f"zh 替换 {_src_text} -> {_json_dst_text}")
            return _json_dst_text
        log.info(f"翻译信息: src_lang={zh_item.src_lang}, dst={zh_item.dst_lang}")
        log.info(f"zh 翻译信息: src={zh_item.src_text}, dst={zh_item.dst_text}")
        log.info(f"en 翻译信息: src={en_item.src_text}, dst={en_item.dst_text}")
        # 机器重新翻译
        # service = self.services.get(get_lang_by_code(zh_item.dst_lang))
        _r = self._translate(
            zh_item.src_lang, zh_item.dst_lang, self.api_tencent_service, zh_item
        )
        log.debug(f"翻译结果: {_r}")
        manual_str = input("请输入人工翻译，此结果会保存: ")
        if manual_str == "zh":
            log.info(f"保留中文翻译结果: {zh_item.dst_text}")
            _r = zh_item.dst_text
        elif manual_str == "en":
            log.info(f"保留英文翻译结果: {zh_item.dst_text}")
            _r = en_item.dst_text
        elif manual_str != "":
            _r = manual_str
        log.info(f"保存翻译结果 {zh_item.src_text} -> {_r}")
        d[_src_text] = _r
        self.json_dict[key] = d
        self.save_json_file()
        return _r
