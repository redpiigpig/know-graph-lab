# -*- coding: utf-8 -*-
"""賀川豐彥（1888–1960）—— NDL 官方 OCR → ja＋繁中的 registry 模組。

貧民窟傳道者與社會運動家，二十世紀日本基督教國際知名度最高的人物。
卒於 1960 → 日本舊法卒後 50 年於 2010 年屆滿、2018 改法不溯及既往 → **日本已 PD**；
台灣 2011 年起 PD。

2026-09-08 以 `scripts/ndl_author_survey.py` 逐筆驗過 NDL：
**自著 92 種全部インターネット公開**（另有編 3、譯 2 未列入）。
這是本 portal 目前最大的一座公有領域礦。

取源與畔上同一條線（`ndl_official_text.py` → `ndl_build.py --build`），
本模組只負責把 `ndl_data/{slug}/secN.json` 交給 `uchimura_auto.py` 翻譯與上架。

見 .claude/skills/ebook-collected-works/ndl_open_scans.md。
"""
from __future__ import annotations

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DATA = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works"

SOURCE_LANG = "ja"
AUTHOR_ZH = "賀川豐彥"
AUTHOR_EN = "Kagawa Toyohiko"
CATEGORY = "神學"
DATA_DIRNAME = "ndl_data"

REGISTRY: dict[str, dict] = {
    "sanjo-no-suikun": {
        # 畔上用 e0000000-…；賀川另起 f0000000-…
        "ebook_id": "f0000000-0000-4000-8000-000000000001",
        "title": "基督山上的垂訓",
        "original_title": "キリスト山上の垂訓",
        "subtitle": "賀川豐彥 1927（NDL 官方 OCR．日文原文＋繁中對照）",
        "year": 1927,
        "parent_volume": "聖書研究與瞑想",
        "ndl_pid": "1187647",
    },
}

QUEUE = ["sanjo-no-suikun"]


def load_work_sections(slug: str) -> list[dict]:
    """讀 ndl_build 產出的 secN.json → [{heading, title_zh, paras}]。"""
    d = _SKILL_DATA / DATA_DIRNAME / slug
    secs = []
    for p in sorted(d.glob("sec*.json"), key=lambda x: int(x.stem[3:])):
        j = json.loads(p.read_text(encoding="utf-8"))
        secs.append({"heading": j["heading"], "title_zh": j.get("title_zh"),
                     "paras": list(j.get("src") or [])})
    if not secs:
        raise RuntimeError(
            "%s 底下沒有 secN.json —— 先跑 ndl_official_text.py 與 ndl_build.py --build" % d)
    return secs


KAGAWA_PROMPT_TMPL = """你是日本近代基督教史的專業譯者，正在翻譯賀川豐彥（1888–1960）
一九二七年的《キリスト山上の垂訓》。原文是戰前日文，直排、舊字體、舊假名遣。
把下列日文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。
3. 舊假名遣（「といふ」「なつてきた」「ゐる」）照現代語意理解，不要逐字直譯成怪中文。
4. **聖經經文與專名照通行中文聖經**：山上寶訓（原題作「垂訓」時保留「垂訓」）、
   八福、天國、馬太福音、路加福音、耶穌、彼得、保羅。
5. 賀川的關鍵語彙照既有定名：貧民窟／合作社（協同組合）／勞工運動／社會事業。
6. 日本事物不可西化：天皇不是皇帝，神社不是廟。
7. 原文兼有講解與勸勉，語氣懇切但不濫情，不要加原文沒有的感嘆。
8. 🚨 遇到表格式的並列（「消極的／積極的」對照、八福逐條）保持條列語感，
   不要改寫成流暢散文，那會把原本的結構弄丟。

日文原文：
{source}"""


def make_engine(backend: str = "auto"):
    """translate_para(ja)->zh。引擎鏈沿用 translate_ebook_to_zh，只換 prompt。"""
    import translate_ebook_to_zh as te
    import uchimura_build as ub
    te.PROMPT_TMPL = KAGAWA_PROMPT_TMPL

    def translate_para(ja: str) -> str:
        src = (ja or "").strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)

        def translate_piece(piece: str) -> str:
            if backend == "haiku":
                return te.haiku_translate(piece)
            if backend == "gemini":
                return te.gemini_translate(piece)
            if backend == "nvidia":
                return te.nvidia_translate(piece)
            return te.gemini_with_nvidia_fallback(piece)

        return ub.clean_zh_output(" ".join(translate_piece(p) for p in pieces))

    return translate_para
